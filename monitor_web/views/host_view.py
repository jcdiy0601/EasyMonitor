#!/usr/bin/env python
# Author: 'JiaChen'


import requests
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
from monitor_web.forms import host_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse


@login_required
def host(request):
    """主机组视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    host_obj_list = models.Host.objects.all()
    host_obj_count = host_obj_list.count()
    page_obj = Page(current_page, host_obj_count)
    host_obj_list = host_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('host.html')
    return render(request, 'host.html', {'host_obj_list': host_obj_list, 'page_str': page_str})


@login_required
def add_host(request):
    """创建主机视图"""
    if request.method == 'GET':
        form_obj = host_form.AddHostForm()
        return render(request, 'add_host.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = host_form.AddHostForm(request.POST)
        if form_obj.is_valid():
            host_group_id_list = form_obj.cleaned_data.pop('host_group_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    host_obj = models.Host.objects.create(**data)
                    host_obj.host_groups.add(*host_group_id_list)
                Logger().log(message='创建主机成功,%s' % host_obj.hostname, mode=True)
                return redirect('/monitor_web/host.html')
            except Exception as e:
                Logger().log(message='创建主机失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加主机失败'), code='invalid')
        else:
            return render(request, 'add_host.html', {'form_obj': form_obj})


@login_required
def hostname_check(request):
    """主机名检测视图"""
    if request.method == 'POST':
        hostname = request.POST.get('hostname')
        ha = hashlib.md5(settings.CMDB_AUTH_KEY.encode('utf-8'))
        timestamp = time.time()
        ha.update(bytes('%s|%f' % (settings.CMDB_AUTH_KEY, timestamp), encoding='utf-8'))
        encrypt = ha.hexdigest()
        result = '%s|%f' % (encrypt, timestamp)
        headers = {settings.CMDB_AUTH_KEY_NAME: result}
        payload = {'hostname': hostname}
        if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", hostname):
            response = {'message': '', 'error': None, 'status': True, 'data': None}
            return JsonResponse(response)
        else:
            response = requests.get(url=settings.CMDB_API_URL, params=payload, headers=headers).json()
            return JsonResponse(response)


@login_required
def edit_host(request, *args, **kwargs):
    """主机组删除视图"""
    hid = kwargs['hid']
    if request.method == 'GET':
        form_obj = host_form.EditHostForm(initial={'hid': hid})
        return render(request, 'edit_host.html', {'form_obj': form_obj, 'hid': hid})
    elif request.method == 'POST':
        form_obj = host_form.EditHostForm(request.POST, initial={'hid': hid})
        if form_obj.is_valid():
            host_group_id_list = form_obj.cleaned_data.pop('host_group_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    host_obj = models.Host.objects.filter(id=hid).first()
                    models.Host.objects.filter(id=hid).update(**data)
                    host_obj.host_groups.set(host_group_id_list)
                Logger().log(message='修改主机成功,%s' % host_obj.hostname, mode=True)
                return redirect('/monitor_web/host.html')
            except Exception as e:
                Logger().log(message='修改主机失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改主机失败'), code='invalid')
        else:
            return render(request, 'edit_host.html', {'form_obj': form_obj, 'hid': hid})


@login_required
def del_host(request):
    """主机组删除视图"""
    if request.method == 'POST':
        response = WebResponse()
        host_list = request.POST.getlist('host_list')
        try:
            with transaction.atomic():
                for host_id in host_list:
                    host_id = int(host_id)
                    host_obj = models.Host.objects.filter(id=host_id).first()
                    host_obj.delete()
                    Logger().log(message='删除主机成功,%s' % host_obj.name, mode=True)
            response.message = '删除主机成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除主机失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
