#!/usr/bin/env python
# Author: 'JiaChen'

from utils.redis_conn import redis_conn
import pickle
from monitor_data import models
from django.core.mail import send_mail
from django.conf import settings
import time
from utils.action_handle import ActionHandle


class TriggerHandle(object):
    """触发器处理"""
    def __init__(self):
        self.settings = settings    # 加载设置
        self.redis_obj = redis_conn(self.settings)  # 获取redis连接实例
        self.alert_counter_dict = {}    # 纪录每个action的触发报警次数
        '''alert_counter_dict = {
            'CentOS-01': {2:{'counter':0,'last_alert':None}, #k CentOS-01是主机名, {2:{'counter'}} 2是trigger id
        }'''
        self.trigger_count = 0  # 触发器计数

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
        self.trigger_count += 1
        trigger_data = pickle.loads(data)
        action_handle_obj = ActionHandle(trigger_data, self.alert_counter_dict)
        action_handle_obj.trigger_process()
