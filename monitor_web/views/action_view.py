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
from monitor_web.forms import action_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn

REDIS_OBJ = redis_conn(settings)


@login_required
def action(request):
    """报警策略视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    action_obj_list = models.Action.objects.all()
    action_obj_count = action_obj_list.count()
    page_obj = Page(current_page, action_obj_count)
    action_obj_list = action_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('action.html')
    return render(request, 'action.html', {'action_obj_list': action_obj_list, 'page_str': page_str})


@login_required
def add_action(request):
    """创建报警策略视图"""
    if request.method == 'GET':
        form_obj = action_form.AddActionForm()
        return render(request, 'add_action.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        print(request.POST)
        form_obj = action_form.AddActionForm(request.POST)
        if form_obj.is_valid():
            trigger_id_list = form_obj.cleaned_data.pop('trigger_id')
            action_operation_id_list = form_obj.cleaned_data.pop('action_operation_id')
            data = form_obj.cleaned_data
            try:
            #     with transaction.atomic():
            #         action_obj = models.HostGroup.objects.create(**data)
            #         action_obj.templates.add(*template_id_list)
            #     Logger().log(message='创建报警策略成功,%s' % action_obj.name, mode=True)
                return redirect('/monitor_web/action.html')
            except Exception as e:
                Logger().log(message='创建报警策略失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加报警策略失败'), code='invalid')

        else:
            return render(request, 'add_action.html', {'form_obj': form_obj})