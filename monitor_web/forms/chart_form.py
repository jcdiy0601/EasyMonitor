#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddChartForm(forms.Form):
    """创建图表表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于64位'},
        label='图表名',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    chart_type = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='图表类型',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('line', '线型图'), ('area', '面积图'), ('pie', '饼图')],
            attrs={'class': 'form-control'}
        )
    )
    templates_id = fields.IntegerField(
        error_messages={'required': '不能为空',
                        'invalid': '格式错误'
                        },
        label='模板',
        help_text='必填项',
        widget=widgets.Select(
            choices=[],
            attrs={'class': 'form-control'}
        )
    )
    item_id = fields.MultipleChoiceField(
        error_messages={'required': '不能为空',
                        'invalid': '格式错误'
                        },
        label='监控项',
        help_text='必填项',
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
        super(AddChartForm, self).__init__(*args, **kwargs)
        self.fields['templates_id'].widget.choices = models.Template.objects.all().values_list('id', 'name')
        item_temp_list = models.Item.objects.values_list('id', 'name', 'key')
        item_list = []
        for item in item_temp_list:
            item_list.append([item[0], '%s %s' % (item[1], item[2])])
        self.fields['item_id'].choices = item_list

    def clean_name(self):
        name = self.cleaned_data.get('name')
        chart_obj = models.Chart.objects.filter(name=name).first()
        if chart_obj:
            raise ValidationError(_('图表%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')


class EditChartForm(forms.Form):
    """编辑图表表单验证类"""
    name = fields.CharField(
        max_length=64,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于64位'},
        label='图表名',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    chart_type = fields.CharField(
        max_length=64,
        error_messages={
            'required': '不能为空',
            'invalid': '格式错误',
            'max_length': '最大长度不能大于64位'
        },
        label='图表类型',
        help_text='必填项',
        widget=widgets.Select(
            choices=[('line', '线型图'), ('area', '面积图'), ('pie', '饼图')],
            attrs={'class': 'form-control'}
        )
    )
    templates_id = fields.IntegerField(
        error_messages={'required': '不能为空',
                        'invalid': '格式错误'
                        },
        label='模板',
        help_text='必填项',
        widget=widgets.Select(
            choices=[],
            attrs={'class': 'form-control'}
        )
    )
    item_id = fields.MultipleChoiceField(
        error_messages={'required': '不能为空',
                        'invalid': '格式错误'
                        },
        label='监控项',
        help_text='必填项',
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
        super(EditChartForm, self).__init__(*args, **kwargs)
        self.cid = self.initial['cid']
        chart_obj = models.Chart.objects.filter(id=self.cid).first()
        self.fields['name'].initial = chart_obj.name
        self.fields['chart_type'].initial = chart_obj.chart_type
        self.fields['templates_id'].widget.choices = models.Template.objects.all().values_list('id', 'name')
        self.fields['templates_id'].initial = chart_obj.templates_id
        item_temp_list = models.Item.objects.values_list('id', 'name', 'key')
        item_list = []
        for item in item_temp_list:
            item_list.append([item[0], '%s %s' % (item[1], item[2])])
        self.fields['item_id'].choices = item_list
        self.fields['item_id'].initial = []
        query_set = models.Chart.objects.filter(id=self.cid).values('items__id')
        for item in query_set:
            self.fields['item_id'].initial.append(item['items__id'])
        self.fields['memo'].initial = chart_obj.memo

    def clean_name(self):
        name = self.cleaned_data.get('name')
        count = models.Chart.objects.exclude(id=self.cid).filter(name=name).count()
        if count:
            raise ValidationError(_('图表%(name)s已存在'), code='invalid', params={'name': name})
        else:
            return self.cleaned_data.get('name')
