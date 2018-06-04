#!/usr/bin/env python
# Author: 'JiaChen'

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from django.conf import settings
from monitor_data import models
from monitor_web.forms import application_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn

REDIS_OBJ = redis_conn(settings)


@login_required
def trigger(request):
    """触发器视图"""
    template_id = request.GET.get('templateid')
    if template_id:
        template_id = int(template_id)
    else:
        template_id = 0
    template_obj_list = models.Template.objects.all()
    template_obj = models.Template.objects.filter(id=template_id).first()
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    if template_obj:
        trigger_obj_list = template_obj.trigger_set.all()
        trigger_obj_count = trigger_obj_list.count()
        page_obj = Page(current_page, trigger_obj_count)
        trigger_obj_list = trigger_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='trigger.html', template_id=template_id)
    else:
        trigger_obj_list = models.Trigger.objects.all()
        trigger_obj_count = trigger_obj_list.count()
        page_obj = Page(current_page, trigger_obj_count)
        trigger_obj_list = trigger_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='trigger.html', template_id=template_id)
    return render(request, 'trigger.html', {'trigger_obj_list': trigger_obj_list,
                                            'page_str': page_str,
                                            'template_obj_list': template_obj_list,
                                            'template_id': template_id})


@login_required
def add_trigger(request):
    """创建触发器视图"""
    if request.method == 'GET':
        form_obj = application_form.AddApplicationForm()
        return render(request, 'add_application.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = application_form.AddApplicationForm(request.POST)
        if form_obj.is_valid():
            item_id_list = form_obj.cleaned_data.pop('item_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    application_obj = models.Application.objects.create(**data)
                    application_obj.items.add(*item_id_list)
                Logger().log(message='创建触发器成功,%s' % application_obj.name, mode=True)
                return redirect('/monitor_web/application.html')
            except Exception as e:
                Logger().log(message='创建触发器失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加触发器失败'), code='invalid')
        else:
            return render(request, 'add_application.html', {'form_obj': form_obj})


@login_required
def edit_trigger(request, *args, **kwargs):
    """编辑触发器视图"""
    aid = kwargs['aid']
    if request.method == 'GET':
        form_obj = application_form.EditApplicationForm(initial={'aid': aid})
        return render(request, 'edit_application.html', {'form_obj': form_obj, 'aid': aid})
    elif request.method == 'POST':
        form_obj = application_form.EditApplicationForm(request.POST, initial={'aid': aid})
        if form_obj.is_valid():
            item_id_list = form_obj.cleaned_data.pop('item_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.Application.objects.filter(id=aid).update(**data)
                    application_obj = models.Application.objects.filter(id=aid).first()
                    application_obj.items.set(item_id_list)
                Logger().log(message='修改触发器成功,%s' % application_obj.name, mode=True)
                return redirect('/monitor_web/application.html')
            except Exception as e:
                Logger().log(message='修改触发器失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改触发器失败'), code='invalid')
        else:
            return render(request, 'edit_application.html', {'form_obj': form_obj, 'aid': aid})


@login_required
def del_trigger(request):
    """删除触发器视图"""
    if request.method == 'POST':
        response = WebResponse()
        trigger_list = request.POST.getlist('trigger_list')
        try:
            with transaction.atomic():
                for trigger_id in trigger_list:
                    trigger_id = int(trigger_id)
                    trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()
                    key_in_redis = '*_trigger_%s' % trigger_obj.id
                    key_list = REDIS_OBJ.keys(key_in_redis)
                    for key in key_list:
                        REDIS_OBJ.delete(key)  # 删除redis中相关监控项
                    alert_counter_redis_key = settings.ALERT_COUNTER_REDIS_KEY
                    alert_counter_data = json.loads(REDIS_OBJ.get(alert_counter_redis_key).decode())
                    for key1, value1 in alert_counter_data.items():
                        for key2, value2 in value1.items():
                            for key3 in list(value2.keys()):
                                if key3 == str(trigger_id):
                                    del alert_counter_data[key1][key2][key3]  # 删除对应主机下的trigger计数
                    trigger_obj.delete()
                    Logger().log(message='删除触发器成功,%s' % trigger_obj.name, mode=True)
            response.message = '删除触发器成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除触发器失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
