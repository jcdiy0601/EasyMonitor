#!/usr/bin/env python
# Author: 'JiaChen'

import time
import json
from monitor_data import models
from utils import action


class ActionHandle(object):
    """负责把达到报警条件的trigger进行分析,并根据action表中的配置来进行报警"""
    def __init__(self, trigger_data, alert_counter_dict_key, redis_obj):
        self.trigger_data = trigger_data
        self.redis_obj = redis_obj
        self.alert_counter_dict_key = alert_counter_dict_key    # 报警计数字典key
        self.alert_counter_dict = json.loads(self.redis_obj.get(self.alert_counter_dict_key).decode())

    def record_log(self, hostname, trigger_data):
        """将报警日志记录到数据库"""
        models.EventLog.objects.create(
            event_type=0,
            hosts=models.Host.objects.filter(hostname=hostname).first(),
            triggers_id=trigger_data.get('trigger_id'),
            log=trigger_data
        )

    def trigger_process(self):
        """分析触发器并报警"""
        '''
        trigger_data = {
            'duration': 256093.23639798164, 
            'msg': '内存不足,[MemUsage_p (25.08% > 20%)]', 
            'hostname': 'CentOS-02_172.16.99.24', 
            'expression_result_list': [
                {'expression_obj': 4, 
                'calc_res_val': 25.08, 
                'specified_item_key': None, 
                'calc_res': True
                }
            ], 
            'trigger_id': 3, 
            'start_time': 1526032489.0128894
        }
        '''
        if self.trigger_data.get('trigger_id') is None:
            if self.trigger_data.get('msg'):
                pass    # 既然没有trigger id直接报警给管理员

        else:   # 正经的trigger报警要触发了
            trigger_id = self.trigger_data.get('trigger_id')    # 获取触发器id
            hostname = self.trigger_data.get('hostname')    # 获取主机名
            trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()  # 获取触发器实例
            action_set = trigger_obj.action_set.all()   # 获取报警策略集合
            for action_obj in action_set:   # 循环每个报警策略
                if action_obj.enabled:  # 这条报警策略启用状态
                    if str(action_obj.id) not in self.alert_counter_dict:    # 第一次被触发，先初始化一个action_counter_dict
                        self.alert_counter_dict[str(action_obj.id)] = {}
                    if hostname not in self.alert_counter_dict[str(action_obj.id)]:  # 这个主机第一次触发这个报警
                        self.alert_counter_dict[str(action_obj.id)][hostname] = {}
                    if str(trigger_id) not in self.alert_counter_dict[str(action_obj.id)][hostname]:
                        self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)] = {"counter": 1, "last_alert": time.time()}
                        for action_operation_obj in action_obj.action_operations.all().order_by('-step'):
                            if self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)]["counter"] >= action_operation_obj.step:     # 报警计数大于报警升级阈值
                                action_func = getattr(action, '%s' % action_operation_obj.action_type)
                                action_func(action_operation_obj, hostname, self.trigger_data, action_obj, status=False)
                                self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)]["last_alert"] = time.time()    # 报完警后更新一下报警时间，这样就又重新计算报警间隔了
                                self.redis_obj.set(self.alert_counter_dict_key, json.dumps(self.alert_counter_dict))
                                self.record_log(hostname, self.trigger_data)  # 记录日志
                    else:
                        # 如果达到报警触发interval次数，就记数+1
                        if time.time() - self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)]["last_alert"] >= action_obj.interval:
                            self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)]["counter"] += 1
                            for action_operation_obj in action_obj.action_operations.all().order_by('-step'):
                                if self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)]["counter"] >= action_operation_obj.step:  # 报警计数大于报警升级阈值
                                    action_func = getattr(action, '%s' % action_operation_obj.action_type)
                                    action_func(action_operation_obj, hostname, self.trigger_data, action_obj, status=False)
                                    self.alert_counter_dict[str(action_obj.id)][hostname][str(trigger_id)]["last_alert"] = time.time()  # 报完警后更新一下报警时间，这样就又重新计算报警间隔了
                                    self.redis_obj.set(self.alert_counter_dict_key, json.dumps(self.alert_counter_dict))
                                    self.record_log(hostname, self.trigger_data)  # 记录日志
