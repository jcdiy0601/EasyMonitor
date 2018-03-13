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


class UserInfoForm(forms.Form):
    """用户信息更改Form表单提交验证类"""
    password1 = forms.CharField(
        max_length=128,
        error_messages={'required': '密码不能为空', 'max_length': '密码长度不能大于128字节'}
    )
    password2 = forms.CharField(
        max_length=128,
        error_messages={'required': '密码不能为空', 'max_length': '密码长度不能大于128字节'}
    )

    def clean(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError(_('两次输入的密码不一致'), code='invalid')
        return self.cleaned_data
