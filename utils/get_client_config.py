#!/usr/bin/env python
# Author: 'JiaChen'

from django.core.exceptions import ObjectDoesNotExist
from monitor_data import models
from utils.log import Logger


class GetClientConfigHandle(object):
    """获取客户端监控配置"""

    def __init__(self, hostname, client_config_dict):
        self.hostname = hostname
        self.client_config_dict = client_config_dict

    def fetch_config(self):
        """获取监控配置"""
        try:
            host_obj = models.Host.objects.filter(hostname=self.hostname).first()
            template_obj_list = list(host_obj.templates.all())  # 获取主机模板列表
            for host_group_obj in host_obj.host_groups.all():   # 主机对应多个模板、主机对应组也对应多个模板，通过这些模板去重才能获取到主机全部的应用集
                template_obj_list.extend(host_group_obj.templates.all())  # 主机模板中添加主机组模板
            template_obj_set = set(template_obj_list)
            for template_obj in template_obj_set:
                for application_obj in template_obj.applications.all():  # 循环每个模板下的应用集
                    self.client_config_dict['data'][application_obj.name] = [application_obj.plugin_name, application_obj.interval]
            self.client_config_dict['code'] = 200
            self.client_config_dict['message'] = '获取监控配置成功'
            Logger().log(message='获取监控配置成功,%s' % self.hostname, mode=True)
        except ObjectDoesNotExist as e:
            self.client_config_dict['code'] = 404
            self.client_config_dict['message'] = '客户端主机名不存在'
            Logger().log(message='客户端主机名不存在,%s' % self.hostname, mode=False)
        return self.client_config_dict
