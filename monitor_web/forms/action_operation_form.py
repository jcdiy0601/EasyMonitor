#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddActionOperationForm(forms.Form):
    """创建报警动作表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='报警动作名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    action_type = fields.CharField(
        error_messages={'invalid': '格式错误'},
        label='动作类型',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('email', '邮件'), ('sms', '短信'), ('weixin', '微信'), ('script', '脚本')],
            attrs={'class': 'form-control'}
        )
    )
    step = fields.IntegerField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
        },
        label='报警升级阈值',
        help_text='必填项',
        widget=widgets.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    user_profile_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='所属用户',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
        )
    )
    script_name = fields.CharField(
        required=False,
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='脚本名称',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
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
        super(AddActionOperationForm, self).__init__(*args, **kwargs)
        self.fields['user_profile_id'].choices = models.UserProfile.objects.values_list('id', 'email')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        action_operation_obj = models.ActionOperation.objects.filter(name=name).first()
        if action_operation_obj:
            raise ValidationError(_('报警动作%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')


class EditActionOperationForm(forms.Form):
    """编辑报警动作表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='报警动作名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    action_type = fields.CharField(
        error_messages={'invalid': '格式错误'},
        label='动作类型',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('email', '邮件'), ('sms', '短信'), ('weixin', '微信'), ('script', '脚本')],
            attrs={'class': 'form-control'}
        )
    )
    step = fields.IntegerField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
        },
        label='报警升级阈值',
        help_text='必填项',
        widget=widgets.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    user_profile_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='所属用户',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
        )
    )
    script_name = fields.CharField(
        required=False,
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='脚本名称',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
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
        super(EditActionOperationForm, self).__init__(*args, **kwargs)
        self.aid = self.initial['aid']
        action_operation_obj = models.ActionOperation.objects.filter(id=self.aid).first()
        self.fields['name'].initial = action_operation_obj.name
        self.fields['action_type'].initial = action_operation_obj.action_type
        self.fields['step'].initial = action_operation_obj.step
        self.fields['user_profile_id'].choices = models.UserProfile.objects.values_list('id', 'email')
        self.fields['user_profile_id'].initial = []
        query_set = models.ActionOperation.objects.filter(id=self.aid).values('user_profiles__id')
        for item in query_set:
            self.fields['user_profile_id'].initial.append(item['user_profiles__id'])
        self.fields['script_name'].initial = action_operation_obj.script_name
        self.fields['memo'].initial = action_operation_obj.memo

    def clean_name(self):
        name = self.cleaned_data.get('name')
        count = models.ActionOperation.objects.exclude(id=self.aid).filter(name=name).count()
        if count:
            raise ValidationError(_('报警动作%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')
