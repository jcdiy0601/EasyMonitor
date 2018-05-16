#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Author: JiaChen

import json
from django import template

register = template.Library()


@register.simple_tag
def error_msg(error_list):
    """
    显示单个字段错误信息
    :param error_list:
    :return:
    """
    error_list = json.loads(error_list)
    if error_list:
        return error_list[0]['message']
    return ''


@register.simple_tag
def all_error_msg(error_list):
    """
    显示整体错误信息
    :param error_list:
    :return:
    """
    error_list = json.loads(error_list)
    if error_list:
        return error_list['__all__'][0]['message']
    return ''
