#!/usr/bin/env python
# Author: 'JiaChen'

import json
import operator
import pickle
import time
import subprocess
import hashlib
import requests
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from monitor_data import models
from utils import action
from utils.redis_conn import redis_conn
from utils.log import Logger


class DataHandle(object):
    """处理应用集下每个触发器"""

    def __init__(self, redis_obj=None):
        self.settings = settings    # 加载配置文件
        self.config_update_interval = 120  # 每120s重新从数据库加载一次配置数据
        self.config_last_loading_time = time.time()  # 配置最后加载时间
        self.host_alive_application_name = 'AgentPing'
        self.data_api = settings.DATA_API  # 获取提交监控数据api
        self.key = settings.KEY  # key
        self.key_name = settings.AUTH_KEY_NAME  # key_name
        if redis_obj:   # 没有传入redis连接就重新连接redis
            self.redis_obj = redis_obj
        else:
            self.redis_obj = redis_conn(settings)

    def load_application_data_and_calculating(self, host_obj, trigger_obj):
        """
        从redis db中获取数据，并根据每个应用集的触发器配置进行计算
        :param host_obj: 主机实例
        :param trigger_obj: 应用集下一个触发器实例
        :param redis_obj: 从外面调用此函数时需传入redis_obj,以减少重复连接
        :return:
        """
        expression_result_list = []  # 最终表达式结果列表
        expression_result_str = ''  # 表达式结果字符串
        temp_expression_list = []   # 先把每个expression的结果算出来放在这个列表里,最后再统一计算这个列表
        for expression_obj in trigger_obj.triggerexpression_set.all().order_by('id'):   # 根据id排序循环触发器下所有触发器表达式
            expression_process_obj = ExpressionProcess(data_handle_obj=self,
                                                       host_obj=host_obj,
                                                       expression_obj=expression_obj)   # 获得表达式处理实例，将data_headle实例、主机实例、表达式实例传入其中
            single_expression_result = expression_process_obj.process()     # 得到单条expression表达式的结果
            if single_expression_result:    # 单条expression表达式的结果为[]，不为False
                temp_expression_list.append(single_expression_result)   # 将单条expression表达式的结果字典添加到临时表达式列表中
                if single_expression_result['expression_obj'].logic_with_next:  # 有and or表示并不是最后一条
                    expression_result_str += str(single_expression_result['calc_res']) + ' ' + \
                        single_expression_result['expression_obj'].logic_with_next + ' '
                else:
                    expression_result_str += str(single_expression_result['calc_res'])
                # 把所有结果为True的expression提出来,报警时你得知道是谁出问题导致trigger触发了
                if single_expression_result['calc_res'] is True:
                    single_expression_result['expression_obj'] = single_expression_result['expression_obj'].id  # 要存到redis里，数据库对象转成id
                    expression_result_list.append(single_expression_result)     # 将单条表达式结果添加到最终表达式结果列表中
        if expression_result_str:
            trigger_result = eval(expression_result_str)    # 计算触发器结果
            if trigger_result:  # 终于走到这一步,该触发报警了
                '''
                host_obj->CentOS-03_172.16.99.25 192.168.222.53
                trigger_obj->内存不足
                expression_result_list->[{'specified_item_key': None, 'calc_res': True, 'expression_obj': 4, 'calc_res_val': 93.98}]
                '''
                msg = self.joint_alert_msg(trigger_obj, expression_result_list)     # 拼接消息
                self.alert_notifier(host_obj=host_obj,
                                    trigger_obj=trigger_obj,
                                    expression_result_list=expression_result_list,
                                    msg=msg)    # 报警通知发布
            else:   # 没有触发报警，这是存在两种情况，要通过检查redis中的trigger key来判断是否需要发送恢复邮件
                self.check_and_alert_recover_notifier(host_obj=host_obj, trigger_obj=trigger_obj)    # 检查报警恢复并通知

    def joint_alert_msg(self, trigger_obj, expression_result_list):
        """拼接报警消息"""
        trigger_name = trigger_obj.name     # 获取触发器名称，如内存不足
        msg = '%s,' % trigger_name
        count = 0   # 设置一个计数器
        for expression_result in expression_result_list:
            count += 1
            specified_item_key = expression_result['specified_item_key']    # 获取特殊的key
            if specified_item_key is None:  # 判断是否为None，如果为None建重置为空字符串
                specified_item_key = ''
            calc_res_val = expression_result['calc_res_val']        # 获取计算结果
            expression_id = expression_result['expression_obj']     # 获取表达式id
            expression_obj = models.TriggerExpression.objects.filter(id=expression_id).first()  # 取表达式实例
            for item in expression_obj.operator_choices:    # 循环获取表达式运算符
                if item[0] == expression_obj.operator:
                    expression_operator = item[1]
            data_unit = expression_obj.items.data_unit
            if not data_unit:
                data_unit = ''
            if count == len(expression_result_list):    # 判断是否为最后一个表达式结果
                if expression_obj.applications.name == self.host_alive_application_name:
                    msg = trigger_name
                else:
                    msg += '%s[%s (%s%s %s %s%s)]' % (specified_item_key,
                                                      expression_obj.items.key,
                                                      calc_res_val,
                                                      data_unit,
                                                      expression_operator,
                                                      expression_obj.threshold,
                                                      data_unit)
            else:
                msg += '%s[%s (%s%s %s %s%s)],' % (specified_item_key,
                                                   expression_obj.items.key,
                                                   calc_res_val,
                                                   data_unit,
                                                   expression_operator,
                                                   expression_obj.threshold,
                                                   data_unit)
        return msg

    def alert_notifier(self, host_obj, trigger_obj, expression_result_list, msg):
        """所有触发报警都需要在这里发布通知"""
        if trigger_obj:
            msg_dict = {
                'hostname': host_obj.hostname,  # 主机名
                'trigger_id': trigger_obj.id,  # 触发器id
                'expression_result_list': expression_result_list,  # 表达式结果列表
                'msg': msg,  # 信息
                'start_time': time.time(),  # 开始时间
                'duration': None  # 持续时间
            }
            # 先把之前的trigger加载回来,获取上次报警的时间,以统计故障持续时间
            trigger_redis_key = 'host_%s_trigger_%s' % (host_obj.hostname, trigger_obj.id)
            old_trigger_data = self.redis_obj.get(trigger_redis_key)  # 获取旧的触发器数据
            if old_trigger_data:  # 不是第一次触发
                old_trigger_data = old_trigger_data.decode()
                trigger_start_time = json.loads(old_trigger_data)['start_time']
                msg_dict['start_time'] = trigger_start_time
                msg_dict['duration'] = time.time() - trigger_start_time
            if host_obj.status != 5:
                host_obj.status = 5  # 将主机状态改为问题
                host_obj.save()
                Logger().log(message='服务器状态改变,%s' % host_obj.hostname, mode=True)
            # 同时在redis中纪录这个trigger,前端页面展示时要统计trigger个数
            self.redis_obj.set(trigger_redis_key, json.dumps(msg_dict))
        else:
            msg_dict = {
                'hostname': host_obj.hostname,  # 主机名
                'trigger_id': trigger_obj,   # 触发器id
                'expression_result_list': expression_result_list,   # 表达式结果列表
                'msg': msg,     # 信息
                'start_time': time.time(),  # 开始时间
                'duration': None    # 持续时间
            }
            host_alive_redis_key = 'host_%s_host_alive' % host_obj.hostname
            old_host_alive_data = self.redis_obj.get(host_alive_redis_key)  # 获取旧的主机检测数据
            if old_host_alive_data:     # 不是第一次触发
                old_host_alive_data = old_host_alive_data.decode()
                host_alive_start_time = json.loads(old_host_alive_data)['start_time']
                msg_dict['start_time'] = host_alive_start_time
                msg_dict['duration'] = time.time() - host_alive_start_time
            self.redis_obj.set(host_alive_redis_key, json.dumps(msg_dict))
        # 发送到队列中
        self.redis_obj.publish(settings.TRIGGER_CHAN, pickle.dumps(msg_dict))

    def check_and_alert_recover_notifier(self, host_obj, trigger_obj):
        """检查报警恢复并通知"""
        trigger_redis_key = 'host_%s_trigger_%s' % (host_obj.hostname, trigger_obj.id)
        trigger_data = self.redis_obj.get(trigger_redis_key)
        if trigger_data:
            trigger_data = json.loads(trigger_data.decode())
            alert_counter_dict_key = settings.ALERT_COUNTER_REDIS_KEY
            alert_counter_dict = json.loads(self.redis_obj.get(alert_counter_dict_key).decode())
            old_alert_counter_dict = deepcopy(alert_counter_dict)
            action_set = trigger_obj.action_set.all()   # 获取报警策略集合
            for action_obj in action_set:   # 循环每个报警策略
                if str(action_obj.id) in alert_counter_dict:   # 如果报警计数字典中存在报警策略id
                    for hostname in alert_counter_dict[str(action_obj.id)]:
                        if host_obj.hostname == hostname:   # 主机也对上了
                            del alert_counter_dict[str(action_obj.id)][hostname]
                            self.redis_obj.set(alert_counter_dict_key, json.dumps(alert_counter_dict))
                            # 删除redis上触发器报警的key
                            self.redis_obj.delete(trigger_redis_key)
                            # 将主机状态改为正常在线
                            host_obj.status = 1
                            host_obj.save()
                            Logger().log(message='服务器状态改变,%s' % host_obj.hostname, mode=True)
                            # 发送恢复通知
                            if action_obj.recover_notice:   # 开启了恢复通知功能
                                action_operation_obj_list = action_obj.action_operations.all()
                                for action_operation_obj in action_operation_obj_list:
                                    if old_alert_counter_dict[str(action_obj.id)][hostname]['counter'] >= action_operation_obj.step:
                                        action_func = getattr(action, '%s' % action_operation_obj.action_type)
                                        action_func(action_operation_obj=action_operation_obj,
                                                    hostname=hostname,
                                                    trigger_data=trigger_data,
                                                    action_obj=action_obj)  # 通过反射发送相关恢复通知

    def looping(self):
        """检测所有主机状态，Agent ping"""
        interval = self.update_interval()
        while True:
            host_obj_list = []
            if time.time() - self.config_last_loading_time > self.config_update_interval:   # 重新加载应用集的监控间隔
                interval = self.update_interval()
            application_obj = models.Application.objects.filter(name=self.host_alive_application_name).first()
            template_obj_list = application_obj.template_set.all()
            for template_obj in template_obj_list:
                host_obj_list.extend(template_obj.host_set.all())
            host_obj_set = set(host_obj_list)
            self.process(host_obj_set)
            time.sleep(interval)

    def update_interval(self):
        """从数据库中监控间隔"""
        application_obj = models.Application.objects.filter(name=self.host_alive_application_name).first()
        interval = application_obj.interval
        return interval

    def process(self, host_obj_set):
        """"""
        pool = ThreadPoolExecutor(20)  # 线程池启动20个线程
        for host_obj in host_obj_set:
            pool.submit(self.run, host_obj)
        pool.shutdown(wait=True)

    def run(self, host_obj):
        # res = subprocess.call('ping %s' % host_obj.ip, shell=True)
        res = subprocess.call('/bin/ping %s -c 1 > /dev/null' % host_obj.ip, shell=True)
        data = {'hostname': host_obj.hostname,
                'data': {'ping': res, 'status': 0},
                'application_name': self.host_alive_application_name}
        headers = {}
        headers.update(self.auth_key())  # 生成api认证的主机头信息
        requests.post(url=self.data_api, json=data, headers=headers)

    def auth_key(self):
        """生成认证串"""
        ha = hashlib.md5(self.key.encode('utf-8'))
        timestamp = time.time()
        ha.update(bytes('%s|%f' % (self.key, timestamp), encoding='utf-8'))
        encrypt = ha.hexdigest()
        result = '%s|%f' % (encrypt, timestamp)
        return {self.key_name: result}


class ExpressionProcess(object):
    """通过不同的方法加载和计算数据"""
    def __init__(self, data_handle_obj, host_obj, expression_obj, specified_item=None):
        """
        :param data_handle_obj: DataHandle 实例
        :param host_obj: 主机实例
        :param expression_obj: 表达式实例
        """
        self.data_handle_obj = data_handle_obj
        self.host_obj = host_obj
        self.expression_obj = expression_obj
        self.latest_data_key_in_redis = 'Data_%s_%s_latest' % (host_obj.hostname, expression_obj.applications.name)     # 最新数据key
        if self.expression_obj.data_calc_func_args:
            self.time_range = json.loads(self.expression_obj.data_calc_func_args)['time']   # 获取要从redis中取多长时间的数据,单位为minute
        else:
            self.time_range = 0

    def process(self):
        """算出单条expression表达式的结果"""

        data_list = self.load_data_from_redis()     # 已经按照用户的配置把数据从redis里取出来了, 比如最近5分钟,或10分钟的数据
        data_calc_func = getattr(self, 'get_%s' % self.expression_obj.data_calc_func)   # 反射计算方法
        single_expression_calc_result_list = data_calc_func(data_list)   # 一个表达式计算结果列表
        if single_expression_calc_result_list:  # 确保上面的条件有正确的返回
            result_dict = {
                'calc_res': single_expression_calc_result_list[0],  # 计算结果True或False
                'calc_res_val': single_expression_calc_result_list[1],  # 具体的值
                'specified_item_key': single_expression_calc_result_list[2],    # 特殊的key，如eth0
                'expression_obj': self.expression_obj,  # 表达式实例
            }
            return result_dict
        else:
            return False

    def load_data_from_redis(self):
        """根据表达式的配置从redis加载数据"""
        data_list = []  # 精确的数据列表
        if self.time_range:     # time_range不为0，取一段时间数据
            time_in_sec = int(self.time_range) * 60     # 换算时间范围分钟->秒
            approximate_data_point = int((time_in_sec + 60) / self.expression_obj.applications.interval)    # 获取一个大概要取的点的数量,+60是默认多取一分钟数据,宁多勿少,多出来的后面会去掉
            approximate_data_list = [
                json.loads(i.decode()) for i in self.data_handle_obj.redis_obj.lrange(
                    self.latest_data_key_in_redis, -approximate_data_point, -1
                )
            ]   # 大概的数据列表
            for point in approximate_data_list:
                '''
                [{'SwapFree': 2031592, 'SwapUsage': 20, 'MemTotal': 493952, 'MemUsage_p': 23.13, 'Buffers': 110700,
                  'MemFree': 57852, 'SwapUsage_p': 0.0, 'SwapTotal': 2031612, 'MemUsage': 114232, 'Cached': 211168},
                 1524535751.7057292]
                '''
                value_dict, save_time = point
                if time.time() - save_time < time_in_sec:     # 时间范围内有效数据
                    data_list.append(point)
        else:   # time_range为0，取最后一次数据
            data_list.append(json.loads(self.data_handle_obj.redis_obj.lrange(self.latest_data_key_in_redis, -1, -1)[0].decode()))
        return data_list

    def get_avg(self, data_list):
        """平均值"""
        clean_data_list = []
        clean_data_dict = {}
        for point in data_list:  # 其实这里列表只有一个值
            value, save_time = point
            if value:
                if 'data' not in value:  # 没有子字典数据
                    clean_data_list.append(value[self.expression_obj.items.key])
                else:  # 有子字典数据
                    for name, value_dict in value['data'].items():  # name->eth0,value_dict->{'t_in': xx, 't_out': xx}
                        if name not in clean_data_dict:
                            clean_data_dict[name] = []
                        clean_data_dict[name].append(value_dict[self.expression_obj.items.key])
        if clean_data_list:  # [23.15, 23.65, 23.22, 24.01, 23.24, 23.7, 23.23, 23.66, 23.23]
            avg_res = round(sum(clean_data_list) / len(clean_data_list), 2)
            return [self.judge(avg_res), avg_res, None]
        elif clean_data_dict:  # {'lo': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'eth0': [0.09, 4.7, 3.3, 2.18, 2.57, 2.86, 2.26, 2.23, 2.23]}
            for name, value_list in clean_data_dict.items():
                clean_data_list = [i for i in value_list]
                avg_res = round(0 if sum(clean_data_list) == 0 else sum(clean_data_list) / len(clean_data_list), 2)
                if self.expression_obj.specified_item_key:  # 监控了特定的指标,比如有多个网卡,但这里只特定监控eth0
                    if name == self.expression_obj.specified_item_key:  # # 就是监控这个特定指标,match上了
                        calc_res = self.judge(avg_res)
                        if calc_res:
                            return [calc_res, avg_res, name]  # 后面的循环不用走了,反正 已经成立了一个了
                else:  # 监控这个服务的所有项, 比如一台机器的多个网卡, 任意一个超过了阈值,都算是有问题的
                    calc_res = self.judge(avg_res)
                    if calc_res:
                        return [calc_res, avg_res, None]
        else:  # 可能是由于最近这个服务没有数据汇报过来,取到的数据为空,所以没办法判断阈值
            return [False, None, None]

    def get_last(self, data_list):
        """最近的值"""
        clean_data_list = []
        clean_data_dict = {}
        for point in data_list:     # 其实这里列表只有一个值
            value, save_time = point
            if value:
                if 'data' not in value:     # 没有子字典数据
                    clean_data_list.append(value[self.expression_obj.items.key])
                else:   # 有子字典数据
                    for name, value_dict in value['data'].items():  # name->eth0,value_dict->{'t_in': xx, 't_out': xx}
                        if name not in clean_data_dict:
                            clean_data_dict[name] = []
                        clean_data_dict[name].append(value_dict[self.expression_obj.items.key])
        if clean_data_list: # [24.16]
            last_res = clean_data_list[0]
            return [self.judge(last_res), last_res, None]
        elif clean_data_dict:   # {'/': [5], '/boot': [8]}
            for name, value_list in clean_data_dict.items():
                clean_data_list = [i for i in value_list]
                last_res = clean_data_list[0]
                if self.expression_obj.specified_item_key:  # 监控了特定的指标,比如有多个网卡,但这里只特定监控eth0
                    if name == self.expression_obj.specified_item_key:  # # 就是监控这个特定指标,match上了
                        calc_res = self.judge(last_res)
                        if calc_res:
                            return [calc_res, last_res, name]   # 后面的循环不用走了,反正 已经成立了一个了
                else:   # 监控这个服务的所有项, 比如一台机器的多个网卡, 任意一个超过了阈值,都 算是有问题的
                    calc_res = self.judge(last_res)
                    if calc_res:
                        return [calc_res, last_res, None]
            else:   # 能走到这一步,代表上面的循环判段都未成立
                return [False, last_res, name]
        else:   # 可能是由于最近这个服务没有数据汇报过来,取到的数据为空,所以没办法判断阈值
            return [False, None, None]

    def judge(self, calculated_value):
        """判断计算后结果是否到达阈值，已经算好的结果,可能是avg(5) or ...."""
        calc_func = getattr(operator, self.expression_obj.operator)
        return calc_func(calculated_value, self.expression_obj.threshold)
