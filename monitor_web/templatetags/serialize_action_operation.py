#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def display_action_type(action_operation_obj):
    """
    显示动作类型
    :param action_operation_obj:
    :return:
    """
    action_operation_list = action_operation_obj.action_type_choices
    for action_type in action_operation_list:
        if action_operation_obj.action_type == action_type[0]:
            return mark_safe(action_type[1])
