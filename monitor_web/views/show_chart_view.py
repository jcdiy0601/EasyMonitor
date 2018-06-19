#!/usr/bin/env python
# Author: 'JiaChen'

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from monitor_data import models
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn


@login_required
def show_chart(request):
    """图形视图"""
    host_group_obj_list = models.HostGroup.objects.all()
    host_obj_list = models.Host.objects.all()
    return render(request, 'show_chart.html', {'host_group_obj_list': host_group_obj_list,
                                               'host_obj_list': host_obj_list})


@login_required
def select_host_group_for_show_chart(request):
    """选择主机组"""
    if request.method == 'POST':
        response = WebResponse()
        host_group_id = request.POST.get('host_group_id')
        host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
        data = list(host_group_obj.host_set.all().values('id', 'ip'))
        response.data = data
        return JsonResponse(response.__dict__)


@login_required
def select_host_for_show_chart(request):
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


@login_required
def select_template_for_show_chart(request):
    """选择模板"""
    if request.method == 'POST':
        response = WebResponse()
        template_id = request.POST.get('template_id')
        template_obj = models.Template.objects.filter(id=template_id).first()
        data = list(template_obj.chart_set.all().values('id', 'name'))
        response.data = data
        return JsonResponse(response.__dict__)


@login_required
def select_chart_for_show_chart(request):
    """选择图表"""
    if request.method == 'POST':
        response = WebResponse()
        data = {}
        chart_id = request.POST.get('chart_id')
        search_time = request.POST.get('search_time')
        chart_obj = models.Chart.objects.filter(id=chart_id).first()
        data['chart_name'] = chart_obj.name
        data['chart_type'] = chart_obj.chart_type
        item_obj_list = chart_obj.items.all()
        for item_obj in item_obj_list:
            pass
        response.data = data
        return JsonResponse(response.__dict__)
