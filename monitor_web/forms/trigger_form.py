#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddTriggerForm(forms.Form):
    """添加触发器表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='触发器名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    templates_id = fields.IntegerField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
        },
        label='模板',
        help_text='必填项',
        widget=widgets.Select(
            choices=[],
            attrs={'class': 'form-control'}
        )
    )
    severity = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='报警级别',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('information', '信息'), ('warning', '警告'), ('general', '一般严重'), ('high', '严重'), ('disaster', '灾难')],
            attrs={'class': 'form-control'}
        )
    )
    enabled = fields.CharField(
        required=False,
        error_messages={
            'invalid': '格式错误',
        },
        label='是否启用',
        help_text='必填项',
        widget=widgets.CheckboxInput()
    )
    memo = fields.CharField(
        required=False,
        error_messages={
            'invalid': '格式错误',
        },
        label='备注',
        widget=widgets.Textarea(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(AddTriggerForm, self).__init__(*args, **kwargs)
        self.fields['templates_id'].widget.choices = models.Template.objects.all().values_list('id', 'name')


class EditTriggerForm(forms.Form):
    """编辑触发器表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='触发器名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    templates_id = fields.IntegerField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
        },
        label='模板',
        help_text='必填项',
        widget=widgets.Select(
            choices=[],
            attrs={'class': 'form-control',
                   'disabled': 'true'}
        )
    )
    severity = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='报警级别',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('information', '信息'), ('warning', '警告'), ('general', '一般严重'), ('high', '严重'), ('disaster', '灾难')],
            attrs={'class': 'form-control'}
        )
    )
    enabled = fields.CharField(
        required=False,
        error_messages={
            'invalid': '格式错误',
        },
        label='是否启用',
        help_text='必填项',
        widget=widgets.CheckboxInput()
    )
    memo = fields.CharField(
        required=False,
        error_messages={
            'invalid': '格式错误',
        },
        label='备注',
        widget=widgets.Textarea(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, *args, **kwargs):
        super(EditTriggerForm, self).__init__(*args, **kwargs)
        self.tid = self.initial['tid']
        trigger_obj = models.Trigger.objects.filter(id=self.tid).first()
        self.fields['templates_id'].widget.choices = models.Template.objects.all().values_list('id', 'name')
        self.fields['name'].initial = trigger_obj.name
        self.fields['templates_id'].initial = trigger_obj.templates_id
        self.fields['severity'].initial = trigger_obj.severity
        self.fields['enabled'].initial = trigger_obj.enabled
        self.fields['memo'].initial = trigger_obj.memo
