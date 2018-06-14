#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddItemForm(forms.Form):
    """添加监控项表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='监控项名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    key = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='键值',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    data_type = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='数据类型',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('int', '整数'), ('float', '小数')],
            attrs={'class': 'form-control'}
        )
    )
    data_unit = fields.CharField(
        required=False,
        max_length=64,
        error_messages={
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='数据单位',
        widget=widgets.Select(
            choices=[('', '无'), ('KB', 'KB'), ('MB', 'MB'), ('GB', 'GB'), ('%', '百分比'), ('KB/s', 'KB/s'), ('MB/s', 'MB/s'),],
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

    def clean_key(self):
        key = self.cleaned_data.get('key')
        item_obj = models.Item.objects.filter(key=key).first()
        if item_obj:
            raise ValidationError(_('监控项%(key)s已存在'), code='invalid', params={'key': key})
        else:
            return self.cleaned_data.get('key')


class EditItemForm(forms.Form):
    """编辑监控项表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='监控项名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    key = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='键值',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    data_type = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='数据类型',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('int', '整数'), ('float', '小数')],
            attrs={'class': 'form-control'}
        )
    )
    data_unit = fields.CharField(
        required=False,
        max_length=64,
        error_messages={
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='数据单位',
        widget=widgets.Select(
            choices=[('', '无'), ('KB', 'KB'), ('MB', 'MB'), ('GB', 'GB'), ('%', '百分比'), ('KB/s', 'KB/s'), ('MB/s', 'MB/s'), ],
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
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.iid = self.initial['iid']
        item_obj = models.Item.objects.filter(id=self.iid).first()
        self.fields['name'].initial = item_obj.name
        self.fields['key'].initial = item_obj.key
        self.fields['data_type'].initial = item_obj.data_type
        self.fields['data_unit'].initial = item_obj.data_unit
        self.fields['memo'].initial = item_obj.memo

    def clean_key(self):
        key = self.cleaned_data.get('key')
        count = models.Item.objects.exclude(id=self.iid).filter(key=key).count()
        if count:
            raise ValidationError(_('监控项%(key)s已存在'), code='invalid', params={'key': key})
        else:
            return self.cleaned_data.get('key')
