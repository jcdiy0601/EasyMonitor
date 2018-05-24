#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def item_count(template_obj):
    """
    获取监控项数量
    :param template_obj:
    :return:
    """
    template_item_list = []
    for application_obj in template_obj.applications.all():
        for items_obj in application_obj.items.all():
            template_item_list.append(items_obj)
    template_item_set = set(template_item_list)
    template_item_count = len(template_item_set)
    return mark_safe(template_item_count)


@register.simple_tag
def display_host(template_obj):
    """
    显示主机
    :param template_obj:
    :return:
    """
    pass
    host_obj_list = []
    for host_obj in template_obj.host_set.all():
        host_obj_list.append(host_obj)
    for host_group_obj in template_obj.hostgroup_set.all():
        for host_obj in host_group_obj.host_set.all():
            host_obj_list.append(host_obj)
    host_obj_set = set(host_obj_list)
    start = 0
    end = len(host_obj_set)
    temp_str = ''
    for host_obj in host_obj_set:
        start += 1
        if start == end:
            temp_str += '<a href="/monitor_web/edit_host_%s.html" style="text-decoration:underline; color: #0e90d2">%s</a>' % (host_obj.id, host_obj.ip)
        else:
            temp_str += '<a href="/monitor_web/edit_host_%s.html" style="text-decoration:underline; color: #0e90d2">%s,</a>' % (host_obj.id, host_obj.ip)
    return mark_safe(temp_str)
