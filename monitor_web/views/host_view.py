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
from monitor_web.forms import host_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn
from utils.permissions import check_permission

REDIS_OBJ = redis_conn(settings)


@login_required
@check_permission
def host(request):
    """主机视图"""
    host_group_id = request.GET.get('groupid')
    if host_group_id:
        host_group_id = int(host_group_id)
    else:
        host_group_id = 0
    host_group_obj_list = models.HostGroup.objects.all()
    host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    if host_group_obj:
        host_obj_list = host_group_obj.host_set.all()
        host_obj_count = host_obj_list.count()
        page_obj = Page(current_page, host_obj_count)
        host_obj_list = host_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='host.html', host_group_id=host_group_id)
    else:   # 没找到相关主机组
        host_obj_list = models.Host.objects.all()
        host_obj_count = host_obj_list.count()
        page_obj = Page(current_page, host_obj_count)
        host_obj_list = host_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='host.html', host_group_id=host_group_id)
    return render(request, 'host.html', {'host_obj_list': host_obj_list,
                                         'page_str': page_str,
                                         'host_group_obj_list': host_group_obj_list,
                                         'host_group_id': host_group_id})


@login_required
@check_permission
def add_host(request):
    """创建主机视图"""
    if request.method == 'GET':
        form_obj = host_form.AddHostForm()
        return render(request, 'add_host.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = host_form.AddHostForm(request.POST)
        if form_obj.is_valid():
            host_group_id_list = form_obj.cleaned_data.pop('host_group_id')
            template_id_list = form_obj.cleaned_data.pop('template_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    host_obj = models.Host.objects.create(**data)
                    host_obj.host_groups.add(*host_group_id_list)
                    if data['monitor_by'] == 'agent':   # 客户端模式要添加默认模板	Template OS Linux, Template App EasyMonitor Agent
                        template_os_linux_id = models.Template.objects.filter(name='Template OS Linux').first().id
                        template_app_easymonitor_agent_id = models.Template.objects.filter(name='Template App EasyMonitor Agent').first().id
                        template_id_list.append(template_os_linux_id)
                        template_id_list.append(template_app_easymonitor_agent_id)
                        host_obj.templates.add(*template_id_list)
                    else:
                        pass
                Logger().log(message='创建主机成功,%s' % host_obj.hostname, mode=True)
                return redirect('/monitor_web/host.html')
            except Exception as e:
                Logger().log(message='创建主机失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加主机失败'), code='invalid')
        else:
            return render(request, 'add_host.html', {'form_obj': form_obj})


@login_required
@check_permission
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
@check_permission
def edit_host(request, *args, **kwargs):
    """修改主机视图"""
    hid = kwargs['hid']
    if request.method == 'GET':
        form_obj = host_form.EditHostForm(initial={'hid': hid})
        return render(request, 'edit_host.html', {'form_obj': form_obj, 'hid': hid})
    elif request.method == 'POST':
        form_obj = host_form.EditHostForm(request.POST, initial={'hid': hid})
        if form_obj.is_valid():
            host_group_id_list = form_obj.cleaned_data.pop('host_group_id')
            template_id_list = form_obj.cleaned_data.pop('template_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    host_obj = models.Host.objects.filter(id=hid).first()
                    old_hostname = host_obj.hostname
                    models.Host.objects.filter(id=hid).update(**data)
                    host_obj.host_groups.set(host_group_id_list)
                    host_obj.templates.set(template_id_list)
                    if data['hostname'] != old_hostname:    # 主机名变更了
                        # 修改redis中相关数据
                        alert_counter_redis_key = settings.ALERT_COUNTER_REDIS_KEY
                        key_in_redis = '*_%s_*' % old_hostname
                        key_list = REDIS_OBJ.keys(key_in_redis)
                        for key in key_list:  # 循环修改trigger key相关数据
                            new_key = key.decode().replace(old_hostname, data['hostname'])
                            REDIS_OBJ.rename(key, new_key)
                        alert_counter_data = json.loads(REDIS_OBJ.get(alert_counter_redis_key).decode())
                        for key, value in alert_counter_data.items():  # 修改报警计数中相关数据
                            for hostname in list(value.keys()):
                                if hostname == old_hostname:
                                    old_data = alert_counter_data[key][old_hostname]
                                    del alert_counter_data[key][hostname]
                                    alert_counter_data[key][data['hostname']] = old_data
                        REDIS_OBJ.set(alert_counter_redis_key, json.dumps(alert_counter_data))
                Logger().log(message='修改主机成功,%s' % host_obj.hostname, mode=True)
                return redirect('/monitor_web/host.html')
            except Exception as e:
                Logger().log(message='修改主机失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改主机失败'), code='invalid')
        else:
            return render(request, 'edit_host.html', {'form_obj': form_obj, 'hid': hid})


@login_required
@check_permission
def del_host(request):
    """删除主机视图"""
    if request.method == 'POST':
        response = WebResponse()
        host_list = request.POST.getlist('host_list')
        try:
            with transaction.atomic():
                for host_id in host_list:
                    host_id = int(host_id)
                    host_obj = models.Host.objects.filter(id=host_id).first()
                    host_obj.delete()
                    # 删除redis中相关数据
                    alert_counter_redis_key = settings.ALERT_COUNTER_REDIS_KEY
                    key_in_redis = '*_%s_*' % host_obj.hostname
                    key_list = REDIS_OBJ.keys(key_in_redis)
                    for key in key_list:    # 循环删除trigger key相关数据
                        REDIS_OBJ.delete(key)
                    alert_counter_data = json.loads(REDIS_OBJ.get(alert_counter_redis_key).decode())
                    for key, value in alert_counter_data.items():   # 删除报警计数中相关数据
                        for hostname in list(value.keys()):
                            if hostname == host_obj.hostname:
                                del alert_counter_data[key][hostname]
                    REDIS_OBJ.set(alert_counter_redis_key, json.dumps(alert_counter_data))
                    Logger().log(message='删除主机成功,%s' % host_obj.hostname, mode=True)
            response.message = '删除主机成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除主机失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
