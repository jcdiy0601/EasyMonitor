#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddHostForm(forms.Form):
    """"""
    hostname = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='主机名称',
        help_text='必填项，Agent方式要与cmdb客户端配置文件中hostname一致，SNMP、API输入管理IP',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    ip = fields.GenericIPAddressField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误'
        },
        label='IP地址',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
