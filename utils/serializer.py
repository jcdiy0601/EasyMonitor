#!/usr/bin/env python
# Author: 'JiaChen'

from monitor_data import models


def get_application_trigger_obj_set(application_name):
    """获取主机相关应用集的触发器集合"""
    trigger_obj_list = []   # 初始化一个触发器列表
    application_obj = models.Application.objects.filter(name=application_name).first()   # 应用集obj
    trigger_expression_obj_list = list(models.TriggerExpression.objects.filter(applications=application_obj).all())
    for trigger_expression_obj in trigger_expression_obj_list:
        trigger_obj_list.append(trigger_expression_obj.triggers)
    return set(trigger_obj_list)
