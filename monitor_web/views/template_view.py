#!/usr/bin/env python
# Author: 'JiaChen'

import requests
import json
import hashlib
import time
import re
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import template_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn


@login_required
def template(request):
    """模板视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    template_obj_list = models.Template.objects.all()
    template_obj_count = template_obj_list.count()
    page_obj = Page(current_page, template_obj_count)
    template_obj_list = template_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('template.html')
    return render(request, 'template.html', {'template_obj_list': template_obj_list, 'page_str': page_str})


@login_required
def add_template(request):
    """创建模板视图"""
    if request.method == 'GET':
        form_obj = template_form.AddTemplateForm()
        return render(request, 'add_template.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = template_form.AddTemplateForm(request.POST)
        if form_obj.is_valid():
            application_id_list = form_obj.cleaned_data.pop('application_id')
            host_id_list = form_obj.cleaned_data.pop('host_id')
            host_group_id_list = form_obj.cleaned_data.pop('host_group_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    template_obj = models.Template.objects.create(**data)
                    template_obj.applications.add(*application_id_list)
                    template_obj.host_set.add(*host_id_list)
                    template_obj.hostgroup_set.add(*host_group_id_list)
                Logger().log(message='创建模板成功,%s' % template_obj.name, mode=True)
                return redirect('/monitor_web/template.html')
            except Exception as e:
                Logger().log(message='创建模板失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加模板失败'), code='invalid')
        else:
            return render(request, 'add_template.html', {'form_obj': form_obj})


@login_required
def edit_template(request, *args, **kwargs):
    """修改模板视图"""
    tid = kwargs['tid']
    if request.method == 'GET':
        form_obj = template_form.EditTemplateForm(initial={'tid': tid})
        return render(request, 'edit_template.html', {'form_obj': form_obj, 'tid': tid})
    elif request.method == 'POST':
        form_obj = template_form.EditTemplateForm(request.POST, initial={'tid': tid})
        if form_obj.is_valid():
            application_id_list = form_obj.cleaned_data.pop('application_id')
            host_id_list = form_obj.cleaned_data.pop('host_id')
            host_group_id_list = form_obj.cleaned_data.pop('host_group_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.Template.objects.filter(id=tid).update(**data)
                    template_obj = models.Template.objects.filter(id=tid).first()
                    template_obj.applications.set(application_id_list)
                    template_obj.host_set.set(host_id_list)
                    template_obj.hostgroup_set.set(host_group_id_list)
                Logger().log(message='修改模板成功,%s' % template_obj.name, mode=True)
                return redirect('/monitor_web/template.html')
            except Exception as e:
                Logger().log(message='修改模板失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改模板失败'), code='invalid')
        else:
            return render(request, 'edit_template.html', {'form_obj': form_obj, 'tid': tid})


@login_required
def del_template(request):
    """删除视图模板"""
    if request.method == 'POST':
        response = WebResponse()
        template_list = request.POST.getlist('template_list')
        try:
            with transaction.atomic():
                for template_id in template_list:
                    template_id = int(template_id)
                    template_obj = models.Template.objects.filter(id=template_id).first()
                    template_obj.delete()
                    Logger().log(message='删除模板成功,%s' % template_obj.name, mode=True)
            response.message = '删除模板成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除模板失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)

