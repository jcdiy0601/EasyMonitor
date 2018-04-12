#!/usr/bin/env python
# Author: 'JiaChen'


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
            pass
        else:   # 汇报数据是无效的
            self.response['code'] = 422
            self.response['message'] = '服务器判定为无效数据,%s' % self.data
            return self.response
