#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddTemplateForm(forms.Form):
    """添加模板表单验证类"""
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
        super(AddTemplateForm, self).__init__(*args, **kwargs)
        self.fields['application_id'].choices = models.Application.objects.values_list('id', 'name')

    def clean_name(self):
        name = self.cleaned_data.get('name')
        template_obj = models.Template.objects.filter(name=name).first()
        if template_obj:
            raise ValidationError(_('模板%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')
