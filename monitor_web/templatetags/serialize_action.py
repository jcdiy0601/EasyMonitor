#!/usr/bin/env python
# Author: 'JiaChen'

from django import template
from django.utils.safestring import mark_safe
from monitor_data import models

register = template.Library()


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