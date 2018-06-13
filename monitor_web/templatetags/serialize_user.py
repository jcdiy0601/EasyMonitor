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
def serialize_operation(uid):
    """
    初始化项目编辑
    :param uid: uid
    :return:
    """
    temp = '<a href="/monitor_web/edit_user_%s.html"><button type="button" class="btn btn-xs btn-danger">编辑</button></a> | ' % uid
    temp += '<a href="/monitor_web/change_pass_user_%s.html"><button type="button" class="btn btn-xs btn-danger">修改密码</button></a> | ' % uid
    temp += '<a href="/monitor_web/change_permission_user_%s.html"><button type="button" class="btn btn-xs btn-danger">修改权限</button></a>' % uid
    return mark_safe(temp)
