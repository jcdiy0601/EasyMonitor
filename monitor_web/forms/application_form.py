#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddApplicationForm(forms.Form):
    """添加应用集表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='应用集名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    plugin_name = fields.CharField(
        required=False,
        max_length=64,
        error_messages={
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='插件名称',
        help_text='请与Agent端名称一致',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    interval = fields.IntegerField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误'
        },
        label='监控间隔',
        help_text='必填项',
        initial=60,
        widget=widgets.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    item_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='监控项',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
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
        super(AddApplicationForm, self).__init__(*args, **kwargs)
        item_list = []
        for item in models.Item.objects.values_list('id', 'name', 'key'):
            item_list.append((item[0], '%s-%s' % (item[1], item[2])))
        self.fields['item_id'].choices = item_list

    def clean_name(self):
        name = self.cleaned_data.get('name')
        application_obj = models.Application.objects.filter(name=name).first()
        if application_obj:
            raise ValidationError(_('应用集%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')


class EditApplicationForm(forms.Form):
    """编辑应用集表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='应用集名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    plugin_name = fields.CharField(
        required=False,
        max_length=64,
        error_messages={
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='插件名称',
        help_text='请与Agent端名称一致',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    interval = fields.IntegerField(
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误'
        },
        label='监控间隔',
        help_text='必填项',
        widget=widgets.NumberInput(
            attrs={'class': 'form-control'}
        )
    )
    item_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='监控项',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
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
        super(EditApplicationForm, self).__init__(*args, **kwargs)
        self.aid = self.initial['aid']
        application_obj = models.Application.objects.filter(id=self.aid).first()
        self.fields['name'].initial = application_obj.name
        self.fields['plugin_name'].initial = application_obj.plugin_name
        self.fields['interval'].initial = application_obj.interval
        item_list = []
        for item in models.Item.objects.values_list('id', 'name', 'key'):
            item_list.append((item[0], '%s-%s' % (item[1], item[2])))
        self.fields['item_id'].choices = item_list
        self.fields['item_id'].initial = []
        query_set = models.Application.objects.filter(id=self.aid).values('items__id')
        for item in query_set:
            self.fields['item_id'].initial.append(item['items__id'])
        self.fields['memo'].initial = application_obj.memo

    def clean_name(self):
        name = self.cleaned_data.get('name')
        count = models.Application.objects.exclude(id=self.aid).filter(name=name).count()
        if count:
            raise ValidationError(_('应用集%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')
