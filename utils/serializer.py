#!/usr/bin/env python
# Author: 'JiaChen'

from monitor_data import models


def get_application_trigger(application_name):
    """获取主机相关应用集的触发器表达式"""
    trigger_list = []
    application_obj = models.Application.objects.filter(name=application_name).first()   # 应用集
    trigger_expression_list = list(models.TriggerExpression.objects.filter(applications=application_obj).all())
    for trigger_expression_obj in trigger_expression_list:
        trigger_list.append(trigger_expression_obj.triggers)
    return set(trigger_list)


