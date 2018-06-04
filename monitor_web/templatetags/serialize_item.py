#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe
from monitor_data import models

register = template.Library()


@register.simple_tag
def item_count(application_obj):
    """
    获取监控项数量
    :param application_obj:
    :return:
    """
    application_item_list = []
    for items_obj in application_obj.items.all():
        application_item_list.append(items_obj)
    application_item_set = set(application_item_list)
    application_item_count = len(application_item_set)
    return mark_safe(application_item_count)


@register.simple_tag
def display_data_type(item_obj, data_type):
    """
    显示数据类型
    :param item_obj: 监控项实例
    :param data_type: 数据类型
    :return:
    """
    data_type_choice_list = item_obj.data_type_choices
    for data_type_choice in data_type_choice_list:
        if data_type == data_type_choice[0]:
            return mark_safe(data_type_choice[1])
