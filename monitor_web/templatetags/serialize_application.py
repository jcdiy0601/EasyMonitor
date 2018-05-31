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
