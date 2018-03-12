#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class AccloginForm(forms.Form):
    """用户登录Form表单提交验证类"""
    email = forms.EmailField(
        max_length=255,
        error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式错误', 'max_length': '邮箱长度不能大于255字节'}
    )
    password = forms.CharField(
        max_length=128,
        error_messages={'required': '密码不能为空', 'max_length': '密码长度不能大于128字节'}
    )
