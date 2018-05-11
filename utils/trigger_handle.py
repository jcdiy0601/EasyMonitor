#!/usr/bin/env python
# Author: 'JiaChen'

import json
import time
import pickle
from django.core.mail import send_mail
from django.conf import settings
from monitor_data import models
from utils.redis_conn import redis_conn
from utils.action_handle import ActionHandle



class TriggerHandle(object):
    """触发器处理"""
    def __init__(self):
        self.settings = settings    # 加载设置
        self.redis_obj = redis_conn(self.settings)  # 获取redis连接实例
        self.alert_counter_dict_key = settings.ALERT_COUNTER_REDIS_KEY  # 报警计数字典key name
        self.redis_obj.set(self.alert_counter_dict_key, '{}')
        '''alert_counter_dict = {
            1: {'CentOS-02_172.16.99.24': {'last_alert': 1525837186.268634, 'counter': 1}}
        }'''

    def start_watching(self):
        """开始监听"""
        radio = self.redis_obj.pubsub()     # 打开收音机
        radio.subscribe(self.settings.TRIGGER_CHAN)     # 调频
        radio.parse_response()  # 准备好开始接收
        while True:
            data = radio.parse_response()[-1]
            self.trigger_consume(data)

    def trigger_consume(self, data):
        """消费订阅到的消息"""
        trigger_data = pickle.loads(data)
        action_handle_obj = ActionHandle(trigger_data, self.alert_counter_dict_key, self.redis_obj)
        action_handle_obj.trigger_process()
