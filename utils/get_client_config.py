#!/usr/bin/env python
# Author: 'JiaChen'

from monitor_data import models
from django.core.exceptions import ObjectDoesNotExist
from utils.log import Logger


class ClientHandle(object):
    """获取客户端监控配置"""
    def __init__(self, hostname):
        self.hostname = hostname
        self.client_configs = {
            'application': {},   # {'application': {'LinuxCpu': ['LinuxCpuPlugin', 30], 'LinuxNetwork': ['LinuxNetworkPlugin', 60], 'LinuxLoad': ['LinuxLoadPlugin', 60], 'LinuxMemory': ['LinuxMemoryPlugin', 60]}}
            'code': None,   # 状态码
            'message': None     # 信息
        }

    def fetch_configs(self):
        """获取监控配置"""
        try:
            host_obj = models.Host.objects.get(hostname=self.hostname)
            template_list = list(host_obj.templates.all())  # 获取主机模板列表
            for host_group in host_obj.hosts_groups.all():
                template_list.extend(host_group.templates.all())    # 主机模板中添加主机组模板
            for template in template_list:
                for application in template.applications.all():     # 循环每个模板下的应用集
                    self.client_configs['application'][application.name] = [application.plugin_name, application.interval]
            self.client_configs['code'] = 200
            self.client_configs['message'] = '获取监控配置成功'
            Logger().log(message='获取监控配置成功,%s' % self.hostname, mode=True)
        except ObjectDoesNotExist as e:
            self.client_configs['code'] = 404
            self.client_configs['message'] = '资源不存在'
            Logger().log(message='资源不存在,%s' % self.hostname, mode=False)
        return self.client_configs
