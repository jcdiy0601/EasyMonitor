#!/usr/bin/env python
# Author: 'JiaChen'

from monitor_data import models
from utils.log import Logger


class DataVerificationHandle(object):
    """数据校验"""
    def __init__(self, hostname, application_name, data):
        self.hostname = hostname
        self.application_name = application_name
        self.data = data
        self.response = {'code': None, 'message': None}

    def check_data(self):
        host_obj = models.Host.objects.filter(hostname=self.hostname).first()
        application_obj = models.Application.objects.filter(name=self.application_name).first()
        if not host_obj:    # 没有这个主机
            self.response['code'] = 404
            self.response['message'] = '客户端主机名不存在'
            Logger().log(message='[%s]客户端主机名不存在' % self.hostname, mode=False)
            return self.response
        if not application_obj:    # 没有应用集
            self.response['code'] = 404
            self.response['message'] = '应用集名称不存在'
            Logger().log(message='[%s]应用集名称不存在' % self.application_name, mode=False)
            return self.response
        if self.data['status'] != 0:    # 无效数据
            self.response['code'] = 422
            self.response['message'] = '服务器判定为无效数据' % self.data
            Logger().log(message='%s,服务器判定为无效数据' % self.data, mode=True)
            return self.response
        else:   # 有效数据
            del self.data['status']
            self.response['code'] = 422