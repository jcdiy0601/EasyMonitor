#!/usr/bin/env python
# Author: 'JiaChen'

from monitor_data import models


class ClientHandler(object):
    """获取客户端监控配置"""
    def __init__(self, hostname):
        self.hostname = hostname
        self.client_configs = {
            'application': {}
        }

    def fetch_configs(self):
        """获取监控配置"""
        try:
            host_obj = models.Hosts.objects.get(hostname=self.hostname)
            template_list = list(host_obj.templates.all())  # 获取主机模板列表
            for host_group in host_obj.hosts_groups.all():
                template_list.extend(host_group.templates.all())    # 主机模板中添加主机组模板
            for template in template_list:
                for application in template.applications.all():     # 循环每个模板下的应用集
                    self.client_configs['application'][application.name] = [application.plugin_name, application.interval]
        except Exception as e:
            pass
        return self.client_configs
