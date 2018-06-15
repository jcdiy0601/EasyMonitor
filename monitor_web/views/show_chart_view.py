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
from monitor_web.forms import host_group_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn
from utils.permissions import check_permission


@login_required
def show_chart(request):
    """图形视图"""
    host_group_obj_list = models.HostGroup.objects.all()
    host_obj_list = models.Host.objects.all()
    return render(request, 'show_chart.html', {'host_group_obj_list': host_group_obj_list,
                                               'host_obj_list': host_obj_list})


def select_host_group_for_chart(request):
    """选择主机组"""
    if request.method == 'POST':
        response = WebResponse()
        host_group_id = request.POST.get('host_group_id')
        host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
        data = list(host_group_obj.host_set.all().values('id', 'ip'))
        response.data = data
        return JsonResponse(response.__dict__)


def select_host_for_chart(request):
    """选择主机"""
    if request.method == 'POST':
        response = WebResponse()
        host_id = request.POST.get('host_id')
        host_group_id = request.POST.get('host_group_id')
        host_obj = models.Host.objects.filter(id=host_id).first()
        host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
        data = list(host_obj.templates.all().values('id', 'name'))
        if host_group_obj:
            for item in list(host_group_obj.templates.all().values('id', 'name')):
                if item not in data:
                    data.append(item)
        response.data = data
        return JsonResponse(response.__dict__)


def select_template_for_chart(request):
    """选择模板"""
    if request.method == 'POST':
        response = WebResponse()
        template_id = request.POST.get('template_id')
        template_obj = models.Template.objects.filter(id=template_id).first()
        data = list(template_obj.chart_set.all().values('id', 'name'))
        response.data = data
        return JsonResponse(response.__dict__)
