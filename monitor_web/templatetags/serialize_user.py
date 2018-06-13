#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe
from monitor_data import models

register = template.Library()


@register.simple_tag
def display_is_active(user_obj):
    """
    显示是否可登录
    :param user_obj:
    :return:
    """
    if user_obj.is_active:
        return mark_safe('<i class="im-checkmark-circle"></i>')
    else:
        return mark_safe('<i class ="im-cancel-circle" ></i>')


@register.simple_tag
def display_is_admin(user_obj):
    """
    显示是否为管理员
    :param user_obj:
    :return:
    """
    if user_obj.is_admin:
        return mark_safe('<i class="im-checkmark-circle"></i>')
    else:
        return mark_safe('<i class ="im-cancel-circle" ></i>')


@register.simple_tag
def serialize_url(table_name, table_object):
    """
    初始化项目编辑
    :param table_name: 表名
    :param table_object: 对象
    :return:
    """
    temp = '<a href="/monitor_web/edit_%s_%s.html"><i class="ec-pencil"></i></a>' % (table_name, table_object.id)
    return mark_safe(temp)
