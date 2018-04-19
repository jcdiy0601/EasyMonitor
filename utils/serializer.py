#!/usr/bin/env python
# Author: 'JiaChen'


def get_host_triggers(host_obj):
    """获取主机的触发器"""
    triggers = []
    for template in host_obj.templates.all():   # 循环主机下所有的模板
        pass