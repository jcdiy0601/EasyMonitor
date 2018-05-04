#!/usr/bin/env python
# Author: 'JiaChen'

from django.conf import settings
import time
from utils.redis_conn import redis_conn
import json
import operator
import pickle
from monitor_data import models


class DataHandle(object):
    """处理应用集下每个触发器"""

    def __init__(self, connect_redis=True):
        self.settings = settings    # 加载配置文件
        # self.poll_interval = 3  # 每3秒进行一次全局轮训
        # self.config_update_interval = 120  # 每120s重新从数据库加载一次配置数据
        # self.config_last_loading_time = time.time()  # 配置最后加载时间
        # self.global_monitor_dic = {}
        # self.exit_flag = False
        if connect_redis:   # True为重新连接redis数据库
            self.redis_obj = redis_conn(settings)

    def load_application_data_and_calculating(self, host_obj, trigger_obj, redis_obj):
        """
        从redis db中获取数据，并根据每个应用集的触发器配置进行计算
        :param host_obj: 主机实例
        :param trigger_obj: 应用集下一个触发器实例
        :param redis_obj: 从外面调用此函数时需传入redis_obj,以减少重复连接
        :return:
        """
        self.redis_obj = redis_obj  # 加载redis实例
        temp_expression_list = []   # 先把每个expression的结果算出来放在这个列表里,最后再统一计算这个列表
        expression_result_list = []     # 最终表达式结果列表
        expression_result_str = ''  # # 表达式结果字符串
        for expression_obj in trigger_obj.triggerexpression_set.all().order_by('id'):   # 根据id排序循环触发器下所有触发器表达式
            expression_process_obj = ExpressionProcess(data_handle_obj=self,
                                                       host_obj=host_obj,
                                                       expression_obj=expression_obj)   # 获得表达式处理实例，将data_headle实例、主机实例、表达式实例传入其中
            single_expression_result = expression_process_obj.process()     # 得到单条expression表达式的结果
            if single_expression_result:    # 结果为[]，不为False
                temp_expression_list.append(single_expression_result)
                if single_expression_result['expression_obj'].logic_with_next:  # 有and or表示并不是最后一条
                    expression_result_str += str(single_expression_result['calc_res']) + ' ' + \
                        single_expression_result['expression_obj'].logic_with_next + ' '
                else:
                    expression_result_str += str(single_expression_result['calc_res'])
                # 把所有结果为True的expression提出来,报警时你得知道是谁出问题导致trigger触发了
                if single_expression_result['calc_res'] is True:
                    single_expression_result['expression_obj'] = single_expression_result['expression_obj'].id  # 要存到redis里，数据库对象转成id
                    expression_result_list.append(single_expression_result)
        if expression_result_str:
            trigger_result = eval(expression_result_str)
            if trigger_result:  # 终于走到这一步,该触发报警了
                self.trigger_notifier(host_obj=host_obj,
                                      trigger_obj=trigger_obj,
                                      expression_result_list=expression_result_list)

    def trigger_notifier(self, host_obj, trigger_obj, expression_result_list, redis_obj=None, msg=None):
        """所有触发报警都需要在这里发布"""
        pass
    #     if redis_obj:   # 从外部调用 时才用的到,为了避免重复调用redis连接
    #         self.redis = redis_obj
    #     msg_dic = {'hostname': host_obj.hostname,
    #                'trigger_id': trigger_id,
    #                'positive_expressions': positive_expressions,
    #                'msg': msg,
    #                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    #                'start_time': time.time(),
    #                'duration': None
    #                }
    #     self.redis.publish(settings.TRIGGER_CHAN, pickle.dumps(msg_dic))
    #     # 先把之前的trigger加载回来,获取上次报警的时间,以统计故障持续时间
    #     trigger_redis_key = 'host_%s_trigger_%s' % (host_obj.hostname, trigger_id)
    #     old_trigger_data = self.redis.get(trigger_redis_key)
    #     if old_trigger_data:
    #         old_trigger_data = old_trigger_data.decode()
    #         trigger_startime = json.loads(old_trigger_data)['start_time']
    #         msg_dic['start_time'] = trigger_startime
    #         msg_dic['duration'] = round(time.time() - trigger_startime)
    #     # 同时在redis中纪录这个trigger,前端页面展示时要统计trigger个数
    #     self.redis.set(trigger_redis_key, json.dumps(msg_dic), 300)  # 一个trigger纪录5分钟后会自动清除,为了在前端统计trigger个数用的
    #
    # def looping(self):
    #     """检测所有主机需要监控的服务的数据有没有按时汇报上来，只做基本检测"""
    #     # get latest report data
    #     self.update_or_load_configs()  # 生成全局的监控配置dict
    #     count = 0
    #     while not self.exit_flag:
    #         print("looping %s".center(50, '-') % count)
    #         count += 1
    #         if time.time() - self.config_last_loading_time >= self.config_update_interval:
    #             print("\033[41;1mneed update configs ...\033[0m")
    #             self.update_or_load_configs()
    #             print("monitor dic", self.global_monitor_dic)
    #         if self.global_monitor_dic:
    #             for h, config_dic in self.global_monitor_dic.items():
    #                 print('handling host:\033[32;1m%s\033[0m' % h)
    #                 for service_id, val in config_dic['services'].items():  # 循环所有要监控的服务
    #                     # print(service_id,val)
    #                     service_obj, last_monitor_time = val
    #                     if time.time() - last_monitor_time >= service_obj.interval:  # reached the next monitor interval
    #                         print(
    #                             "\033[33;1mserivce [%s] has reached the monitor interval...\033[0m" % service_obj.name)
    #                         self.global_monitor_dic[h]['services'][service_obj.id][1] = time.time()
    #                         # self.load_service_data_and_calulating(h,service_obj)
    #                         # only do basic data validataion here, alert if the client didn't report data to server in \
    #                         # the configured time interval
    #                         self.data_point_validation(h, service_obj)  # 检测此服务最近的汇报数据
    #                     else:
    #                         next_monitor_time = time.time() - last_monitor_time - service_obj.interval
    #                         print("service [%s] next monitor time is %s" % (service_obj.name, next_monitor_time))
    #
    #                 if time.time() - self.global_monitor_dic[h]['status_last_check'] > 10:
    #                     # 检测 有没有这个机器的trigger,如果没有,把机器状态改成ok
    #                     trigger_redis_key = "host_%s_trigger*" % (h.id)
    #                     trigger_keys = self.redis.keys(trigger_redis_key)
    #                     # print('len grigger keys....',trigger_keys)
    #                     if len(trigger_keys) == 0:  # 没有trigger被触发,可以把状态改为ok了
    #                         h.status = 1
    #                         h.save()
    #                         # looping triggers 这里是真正根据用户的配置来监控了
    #                         # for trigger_id,trigger_obj in config_dic['triggers'].items():
    #                         #    #print("triggers expressions:",trigger_obj.triggerexpression_set.select_related())
    #                         #    self.load_service_data_and_calulating(h,trigger_obj)
    #
    #         time.sleep(self.poll_interval)
    #
    # def update_or_load_configs(self):
    #     '''
    #     load monitor configs from Mysql DB
    #     :return:
    #     '''
    #     all_enabled_hosts = models.Host.objects.all()
    #     for h in all_enabled_hosts:
    #         if h not in self.global_monitor_dic:  # new host
    #             self.global_monitor_dic[h] = {'services': {}, 'triggers': {}}
    #             '''self.global_monitor_dic ={
    #                 'h1':{'services'{'cpu':[cpu_obj,0],
    #                                  'mem':[mem_obj,0]
    #                                  },
    #                       'trigger':{t1:t1_obj,}
    #                     }
    #             }'''
    #         # print(h.host_groups.select_related())
    #         service_list = []
    #         trigger_list = []
    #         for group in h.host_groups.select_related():
    #             # print("grouptemplates:", group.templates.select_related())
    #
    #             for template in group.templates.select_related():
    #                 # print("tempalte:",template.services.select_related())
    #                 # print("triigers:",template.triggers.select_related())
    #                 service_list.extend(template.services.select_related())
    #                 trigger_list.extend(template.triggers.select_related())
    #             for service in service_list:
    #                 if service.id not in self.global_monitor_dic[h]['services']:  # first loop
    #                     self.global_monitor_dic[h]['services'][service.id] = [service, 0]
    #                 else:
    #                     self.global_monitor_dic[h]['services'][service.id][0] = service
    #             for trigger in trigger_list:
    #                 # if not self.global_monitor_dic['triggers'][trigger.id]:
    #                 self.global_monitor_dic[h]['triggers'][trigger.id] = trigger
    #
    #         # print(h.templates.select_related() )
    #         # print('service list:',service_list)
    #
    #         for template in h.templates.select_related():
    #             service_list.extend(template.services.select_related())
    #             trigger_list.extend(template.triggers.select_related())
    #         for service in service_list:
    #             if service.id not in self.global_monitor_dic[h]['services']:  # first loop
    #                 self.global_monitor_dic[h]['services'][service.id] = [service, 0]
    #             else:
    #                 self.global_monitor_dic[h]['services'][service.id][0] = service
    #         for trigger in trigger_list:
    #             self.global_monitor_dic[h]['triggers'][trigger.id] = trigger
    #         # print(self.global_monitor_dic[h])
    #         # 通过这个时间来确定是否需要更新主机状态
    #         self.global_monitor_dic[h].setdefault('status_last_check', time.time())
    #
    #     self.config_last_loading_time = time.time()
    #     return True
    #
    # def data_point_validation(self, host_obj, service_obj):
    #     '''
    #     only do basic data validation here, alert if the client didn't report data to server in the configured time interval
    #     :param h:
    #     :param service_obj:
    #     :return:
    #     '''
    #     service_redis_key = "StatusData_%s_%s_latest" %(host_obj.id,service_obj.name) #拼出此服务在redis中存储的对应key
    #     latest_data_point = self.redis.lrange(service_redis_key,-1,-1)
    #     if latest_data_point: #data list is not empty,
    #         latest_data_point = json.loads(latest_data_point[0].decode())
    #         #print('laste::::',latest_data_point)
    #         print("\033[41;1mlatest data point\033[0m %s" % latest_data_point)
    #         latest_service_data,last_report_time = latest_data_point
    #         monitor_interval = service_obj.interval + self.settings.REPORT_LATE_TOLERANCE_TIME
    #         if time.time() - last_report_time > monitor_interval: #超过监控间隔但数据还没汇报过来,something wrong with client
    #             no_data_secs =  time.time() - last_report_time
    #             msg = '''Some thing must be wrong with client [%s] , because haven't receive data of service [%s] \
    #             for [%s]s (interval is [%s])\033[0m''' %(host_obj.ip_addr, service_obj.name,no_data_secs, monitor_interval)
    #             self.trigger_notifier(host_obj=host_obj,trigger_id=None,positive_expressions=None,
    #                                   msg=msg)
    #             print("\033[41;1m%s\033[0m" %msg )
    #             if service_obj.name == 'uptime': #监控主机存活的服务
    #                 host_obj.status = 3 #unreachable
    #                 host_obj.save()
    #             else:
    #                 host_obj.status = 5 #problem
    #                 host_obj.save()
    #
    #     else: # no data at all
    #         print("\033[41;1m no data for serivce [%s] host[%s] at all..\033[0m" %(service_obj.name,host_obj.name))
    #         msg = '''no data for serivce [%s] host[%s] at all..''' %(service_obj.name,host_obj.name)
    #         self.trigger_notifier(host_obj=host_obj,trigger_id=None,positive_expressions=None,msg=msg)
    #         host_obj.status = 5 #problem
    #         host_obj.save()
    #     #print("triggers:", self.global_monitor_dic[host_obj]['triggers'])


class ExpressionProcess(object):
    """通过不同的方法加载和计算数据"""
    def __init__(self, data_handle_obj, host_obj, expression_obj, specified_item=None):
        """
        :param data_handle_obj: DataHandle 实例
        :param host_obj: 主机实例
        :param expression_obj: 表达式实例
        """
        self.host_obj = host_obj
        self.expression_obj = expression_obj
        self.data_handle_obj = data_handle_obj
        self.latest_data_key_in_redis = 'Data_%s_%s_latest' % (host_obj.hostname, expression_obj.applications.name)     # 最新数据key
        if self.expression_obj.data_calc_func_args:
            self.time_range = json.loads(self.expression_obj.data_calc_func_args)['time']   # 获取要从redis中取多长时间的数据,单位为minute
        else:
            self.time_range = 0

    def load_data_from_redis(self):
        """根据表达式的配置从redis加载数据"""
        data_list = []  # 精确的数据列表
        if self.time_range:
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
        else:
            data_list.append(json.loads(self.data_handle_obj.redis_obj.lrange(self.latest_data_key_in_redis, -1, -1)[0].decode()))
        return data_list

    def process(self):
        """算出单条expression表达式的结果"""

        data_list = self.load_data_from_redis()     # 已经按照用户的配置把数据从redis里取出来了, 比如最近5分钟,或10分钟的数据
        data_calc_func = getattr(self, 'get_%s' % self.expression_obj.data_calc_func)   # 反射计算方法
        single_expression_calc_result_list = data_calc_func(data_list)   # 一个表达式计算结果列表
        # print(self.expression_obj, self.expression_obj.items.key, single_expression_calc_result_list)
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
                else:  # 监控这个服务的所有项, 比如一台机器的多个网卡, 任意一个超过了阈值,都 算是有问题的
                    calc_res = self.judge(avg_res)
                    if calc_res:
                        return [calc_res, avg_res, None]
            else:  # 能走到这一步,代表上面的循环判段都未成立
                return [False, avg_res, name]
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
