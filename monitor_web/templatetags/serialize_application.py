#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe

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
