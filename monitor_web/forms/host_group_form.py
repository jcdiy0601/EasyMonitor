#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddHostGroupForm(forms.Form):
    """添加主机组表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='主机组名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    template_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='模板',
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
        super(AddHostGroupForm, self).__init__(*args, **kwargs)
        self.fields['template_id'].choices = models.Template.objects.values_list('id', 'name')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        host_group_obj = models.HostGroup.objects.filter(name=name).first()
        if host_group_obj:
            raise ValidationError(_('主机组%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')


class EditHostGroupForm(forms.Form):
    """编辑主机组表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='主机组名称',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    template_id = fields.MultipleChoiceField(
        required=False,
        error_messages={'invalid': '格式错误'},
        label='模板',
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
        super(EditHostGroupForm, self).__init__(*args, **kwargs)
        self.gid = self.initial['gid']
        host_group_obj = models.HostGroup.objects.filter(id=self.gid).first()
        self.fields['name'].initial = host_group_obj.name
        self.fields['template_id'].choices = models.Template.objects.values_list('id', 'name')
        self.fields['template_id'].initial = []
        query_set = models.HostGroup.objects.filter(id=self.gid).values('templates__id')
        for item in query_set:
            self.fields['template_id'].initial.append(item['templates__id'])
        self.fields['memo'].initial = host_group_obj.memo

    def clean_name(self):
        name = self.cleaned_data.get('name')
        count = models.HostGroup.objects.exclude(id=self.gid).filter(name=name).count()
        if count:
            raise ValidationError(_('主机组%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')
