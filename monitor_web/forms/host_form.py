#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddHostForm(forms.Form):
    """创建主机表单验证类"""
    hostname = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='主机名称',
        help_text='必填项，Agent与cmdb配置hostname一致（只对Agent做检测），SNMP、API输入管理IP',
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
    host_group_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='主机组',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
        )
    )
    monitor_by = fields.CharField(
        error_messages={'invalid': '格式错误'},
        label='监控方式',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('agent', '客户端'), ('snmp', 'SNMP'), ('api', 'API')],
            attrs={'class': 'form-control'}
        )
    )
    status = fields.IntegerField(
        error_messages={'invalid': '格式错误'},
        label='主机状态',
        help_text='必填项',
        widget=widgets.Select(
            choices=[(3, '未知')],
            attrs={'class': 'form-control'}
        )
    )
    host_alive_check_interval = fields.IntegerField(
        error_messages={'invalid': '格式错误'},
        label='主机存活状态检测间隔(s)',
        help_text='必填项',
        initial=30,
        widget=widgets.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    memo = fields.CharField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='备注',
        widget=widgets.Textarea(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(AddHostForm, self).__init__(*args, **kwargs)
        self.fields['host_group_id'].choices = models.HostGroup.objects.values_list('id', 'name')

    def clean_hostname(self):
        hostname = self.cleaned_data.get('hostname')
        host_obj = models.Host.objects.filter(hostname=hostname).all()
        if host_obj:
            raise ValidationError(_('主机名%(hostname)s已存在'), code='invalid', params={'hostname': hostname})
        else:
            return self.cleaned_data.get('hostname')
