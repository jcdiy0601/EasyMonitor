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
    temp = '<a href="/monitor_web/edit_%s_%s.html"><i class="fa fa-edit"></i></a>' % (table_name, table_object.id)
    return mark_safe(temp)


@register.simple_tag
def application_count(host_obj):
    """
    获取主机应用集数量
    :param host_obj: 主机对象
    :return:
    """
    host_application_list = []
    host_template_list = list(host_obj.templates.all())
    host_group_list = host_obj.host_groups.all()
    for host_group_obj in host_group_list:
        host_group_template_list = host_group_obj.templates.all()
        host_template_list.extend(host_group_template_list)
    host_template_set = set(host_template_list)
    for template_obj in host_template_set:
        host_application_list.extend(template_obj.applications.all())
    host_application_count = len(set(host_application_list))
    return mark_safe(host_application_count)


@register.simple_tag
def item_count(host_obj):
    """
    获取主机监控项数量
    :param host_obj: 主机对象
    :return:
    """
    host_application_list = []
    host_item_list = []
    host_template_list = list(host_obj.templates.all())
    host_group_list = host_obj.host_groups.all()
    for host_group_obj in host_group_list:
        host_group_template_list = host_group_obj.templates.all()
        host_template_list.extend(host_group_template_list)
    host_template_set = set(host_template_list)
    for template_obj in host_template_set:
        host_application_list.extend(template_obj.applications.all())
    host_application_set = set(host_application_list)
    for application_obj in host_application_set:
        host_item_list.extend(application_obj.items.all())
    host_item_count = len(set(host_item_list))
    return mark_safe(host_item_count)


@register.simple_tag
def trigger_count(host_obj):
    """
    获取主机触发器数量
    :param host_obj: 主机对象
    :return:
    """
    host_trigger_list = []
    host_template_list = list(host_obj.templates.all())
    host_group_list = host_obj.host_groups.all()
    for host_group_obj in host_group_list:
        host_group_template_list = host_group_obj.templates.all()
        host_template_list.extend(host_group_template_list)
    host_template_set = set(host_template_list)
    for template_obj in host_template_set:
        host_trigger_list.extend(template_obj.trigger_set.all())
    host_trigger_count = len(set(host_trigger_list))
    return mark_safe(host_trigger_count)


@register.simple_tag
def template_display(host_obj):
    """
    显示主机模板
    :param host_obj: 主机对象
    :return:
    """
    host_template_list = list(host_obj.templates.all())
    host_group_list = host_obj.host_groups.all()
    for host_group_obj in host_group_list:
        host_group_template_list = host_group_obj.templates.all()
        host_template_list.extend(host_group_template_list)
    host_template_set = set(host_template_list)
    temp = ''
    count = 0
    for template_obj in host_template_set:
        count += 1
        if count == len(host_template_set):
            temp += '<a href = "/monitor_web/edit_template_%s.html" style="text-decoration:underline; color: #0e90d2"> %s </a>' % (template_obj.id, template_obj.name)
        else:
            temp += '<a href = "/monitor_web/edit_template_%s.html" style="text-decoration:underline; color: #0e90d2"> %s, </a>' % (template_obj.id, template_obj.name)
    return mark_safe(temp)
