#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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



