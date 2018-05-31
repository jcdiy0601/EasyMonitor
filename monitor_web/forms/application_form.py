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


class EditTemplateForm(forms.Form):
    """编辑模板表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='模板名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    application_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='应用集',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
        )
    )
    host_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='主机',
        choices=[],
        widget=widgets.SelectMultiple(
            attrs={'class': 'form-control',
                   'size': 10}
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
        super(EditTemplateForm, self).__init__(*args, **kwargs)
        self.tid = self.initial['tid']
        template_obj = models.Template.objects.filter(id=self.tid).first()
        self.fields['name'].initial = template_obj.name
        self.fields['application_id'].choices = models.Application.objects.values_list('id', 'name')
        self.fields['application_id'].initial = []
        query_set = models.Template.objects.filter(id=self.tid).values('applications__id')
        for item in query_set:
            self.fields['application_id'].initial.append(item['applications__id'])
        self.fields['host_id'].choices = models.Host.objects.values_list('id', 'hostname')
        self.fields['host_id'].initial = []
        query_set = models.Template.objects.filter(id=self.tid).values('host__id')
        for item in query_set:
            self.fields['host_id'].initial.append(item['host__id'])
        self.fields['host_group_id'].choices = models.HostGroup.objects.values_list('id', 'name')
        self.fields['host_group_id'].initial = []
        query_set = models.Template.objects.filter(id=self.tid).values('hostgroup__id')
        for item in query_set:
            self.fields['host_group_id'].initial.append(item['hostgroup__id'])
        self.fields['memo'].initial = template_obj.memo

    def clean_name(self):
        name = self.cleaned_data.get('name')
        count = models.Template.objects.exclude(id=self.tid).filter(name=name).count()
        if count:
            raise ValidationError(_('模板%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')
