#!/usr/bin/env python
# Author: 'JiaChen'

from django import forms
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models


class AddUserForm(forms.Form):
    """创建用户表单验证类"""
    email = fields.EmailField(
        error_messages={'required': '不能为空', 'invalid': '格式错误'},
        label='邮箱',
        help_text='必填项',
        widget=widgets.EmailInput(
            attrs={'class': 'form-control'}
        )
    )
    name = fields.CharField(
        max_length=64,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于64位'},
        label='姓名',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    phone = fields.CharField(
        required=False,
        max_length=11,
        min_length=11,
        error_messages={'invalid': '格式错误', 'max_length': '最大长度不能大于11位', 'min_length': '最小长度不能小于11位'},
        label='手机号',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    weixin = fields.CharField(
        required=False,
        max_length=64,
        error_messages={'invalid': '格式错误', 'max_length': '最大长度不能大于64位'},
        label='微信号',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    password = fields.CharField(
        max_length=128,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于128位'},
        label='密码',
        help_text='必填项',
        widget=widgets.PasswordInput(
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_obj = models.UserProfile.objects.filter(email=email).first()
        if user_obj:
            raise ValidationError(_('用户%(email)s已存在'), code='invalid', params={'email': email})
        else:
            return self.cleaned_data.get('email')


class EditUserForm(forms.Form):
    """编辑用户表单验证类"""
    email = fields.EmailField(
        error_messages={'required': '不能为空', 'invalid': '格式错误'},
        label='邮箱',
        help_text='必填项',
        widget=widgets.EmailInput(
            attrs={'class': 'form-control'}
        )
    )
    name = fields.CharField(
        max_length=64,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于64位'},
        label='姓名',
        help_text='必填项',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    phone = fields.CharField(
        required=False,
        max_length=11,
        min_length=11,
        error_messages={'invalid': '格式错误', 'max_length': '最大长度不能大于11位', 'min_length': '最小长度不能小于11位'},
        label='手机号',
        widget=widgets.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    weixin = fields.CharField(
        required=False,
        max_length=64,
        error_messages={'invalid': '格式错误', 'max_length': '最大长度不能大于64位'},
        label='微信号',
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
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.uid = self.initial['uid']
        user_obj = models.UserProfile.objects.filter(id=self.uid).first()
        self.fields['email'].initial = user_obj.email
        self.fields['name'].initial = user_obj.name
        self.fields['phone'].initial = user_obj.phone
        self.fields['weixin'].initial = user_obj.weixin
        self.fields['memo'].initial = user_obj.memo

    def clean_email(self):
        email = self.cleaned_data.get('email')
        count = models.UserProfile.objects.exclude(id=self.uid).filter(email=email).count()
        if count:
            raise ValidationError(_('邮箱%(email)s已存在'), code='invalid', params={'email': email})
        else:
            return self.cleaned_data.get('email')


class ChangePassUser(forms.Form):
    """
    修改用户密码视图表单验证类
    """
    password = fields.CharField(
        max_length=128,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于128位'},
        label='密码',
        help_text='必填项',
        widget=widgets.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    password2 = fields.CharField(
        max_length=128,
        error_messages={'required': '不能为空', 'invalid': '格式错误', 'max_length': '最大长度不能大于128位'},
        label='确认密码',
        help_text='必填项',
        widget=widgets.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise ValidationError(_('两次输入的密码不一致'), code='invalid')
        else:
            return self.cleaned_data
