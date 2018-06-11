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
def display_severity(trigger_obj, severity):
    """
    显示报警级别
    :param trigger_obj:
    :param severity:
    :return:
    """
    severity_choices_list = trigger_obj.severity_choices
    for severity_choices in severity_choices_list:
        if severity == severity_choices[0]:
            return mark_safe(severity_choices[1])


@register.simple_tag
def display_enabled(enabled):
    """
    显示是否启用
    :param enabled:
    :return:
    """
    if enabled:
        return mark_safe('<i class="im-checkmark-circle"></i>')
    else:
        return mark_safe('<i class ="im-cancel-circle" ></i>')