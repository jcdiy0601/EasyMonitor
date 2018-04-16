#!/usr/bin/env python
# Author: 'JiaChen'

from django.conf import settings
import json
import time


class DataStore(object):
    """处理客户端报告的服务数据，做一些数据优化并将其保存到redis数据库中"""
    def __init__(self, hostname, application_name, data, redis_obj, response):
        self.hostname = hostname
        self.application_name = application_name
        self.data = data
        self.redis_obj = redis_obj
        self.response = response
        self.process_and_save()

    def process_and_save(self):
        """处理并保存数据到redis中"""
        if self.data['status'] == 0:    # 汇报数据是有效的
            for key, value in settings.DATA_OPTIMIZATION.items():
                data_optimize_interval, max_data_point = value  # 获取数据优化间隔和最大存储点
                data_key_in_redis = 'StatusData_%s_%s_%s' % (self.hostname, self.application_name, key)     # 获取对应主机应用集下的key名称
                print(data_key_in_redis)
                last_point_from_redis = self.redis_obj.lrange(name=data_key_in_redis, start=-1, end=-1)     # 取key最后一个点的值
                if not last_point_from_redis:   # 这个key在redis中不存在
                    # 所以初始化一个新键，数据集中的第一个数据点只会被用来识别上次数据被保存的时候
                    self.redis_obj.rpush(data_key_in_redis, json.dumps([None, time.time()]))
                if data_optimize_interval == 0:     # 这个数据集用于未优化的数据，只有最新的数据不需要优化
                    self.redis_obj.rpush(data_key_in_redis, json.dumps([self.data, time.time()]))
                else:   # 需要优化的数据
                    last_point_data, last_point_save_time = json.loads(self.redis_obj.lrange(name=data_key_in_redis, start=-1, end=-1)[0])
        else:   # 汇报数据是无效的
            self.response['code'] = 422
            self.response['message'] = '服务器判定为无效数据,%s' % self.data
            return self.response
