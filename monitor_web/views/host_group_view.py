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

REDIS_OBJ = redis_conn(settings)


@login_required
@check_permission
def host_group(request):
    """主机组视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    host_group_obj_list = models.HostGroup.objects.all()
    host_group_obj_count = host_group_obj_list.count()
    page_obj = Page(current_page, host_group_obj_count)
    host_group_obj_list = host_group_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('host_group.html')
    return render(request, 'host_group.html', {'host_group_obj_list': host_group_obj_list, 'page_str': page_str})


@login_required
@check_permission
def add_host_group(request):
    """添加主机组视图"""
    if request.method == 'GET':
        form_obj = host_group_form.AddHostGroupForm()
        return render(request, 'add_host_group.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = host_group_form.AddHostGroupForm(request.POST)
        if form_obj.is_valid():
            template_id_list = form_obj.cleaned_data.pop('template_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    host_group_obj = models.HostGroup.objects.create(**data)
                    host_group_obj.templates.add(*template_id_list)
                Logger().log(message='创建主机组成功,%s' % host_group_obj.name, mode=True)
                return redirect('/monitor_web/host_group.html')
            except Exception as e:
                Logger().log(message='创建主机组失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加主机组失败'), code='invalid')
        else:
            return render(request, 'add_host_group.html', {'form_obj': form_obj})


@login_required
@check_permission
def edit_host_group(request, *args, **kwargs):
    """修改主机组视图"""
    gid = kwargs['gid']
    if request.method == 'GET':
        form_obj = host_group_form.EditHostGroupForm(initial={'gid': gid})
        return render(request, 'edit_host_group.html', {'form_obj': form_obj, 'gid': gid})
    elif request.method == 'POST':
        form_obj = host_group_form.EditHostGroupForm(request.POST, initial={'gid': gid})
        if form_obj.is_valid():
            template_id_list = form_obj.cleaned_data.pop('template_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.HostGroup.objects.filter(id=gid).update(**data)
                    host_group_obj = models.HostGroup.objects.filter(id=gid).first()
                    host_group_obj.templates.set(template_id_list)
                Logger().log(message='修改主机组成功,%s' % host_group_obj.name, mode=True)
                return redirect('/monitor_web/host_group.html')
            except Exception as e:
                Logger().log(message='修改主机组失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改主机组失败'), code='invalid')
        else:
            return render(request, 'edit_host_group.html', {'form_obj': form_obj, 'gid': gid})


@login_required
@check_permission
def del_host_group(request):
    """删除主机组视图"""
    if request.method == 'POST':
        response = WebResponse()
        host_group_list = request.POST.getlist('host_group_list')
        try:
            with transaction.atomic():
                for host_group_id in host_group_list:
                    host_group_id = int(host_group_id)
                    host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
                    # 删除这个主机组所有主机自身不存在的监控配置（主机组的监控配置而主机没有相同配置）
                    alert_counter_redis_key = settings.ALERT_COUNTER_REDIS_KEY
                    host_group_template_obj_set = set(host_group_obj.templates.all())
                    host_obj_list = host_group_obj.host_set.all()
                    for host_obj in host_obj_list:
                        host_template_obj_set = set(host_obj.templates.all())
                        only_template_obj_set = host_group_template_obj_set - host_template_obj_set     # 差集，只有主机组关联的模板
                        for template_obj in only_template_obj_set:  # 循环每个模板
                            application_obj_list = template_obj.applications.all()
                            for application_obj in application_obj_list:
                                key_in_redis = '*_%s_%s_*' % (host_obj.hostname, application_obj.name)
                                key_list = REDIS_OBJ.keys(key_in_redis)
                                for key in key_list:
                                    REDIS_OBJ.delete(key)   # 删除redis中相关监控项和报警trigger的key
                            template_trigger_id_list = []
                            template_trigger_obj_list = template_obj.trigger_set.all()
                            for trigger_obj in template_trigger_obj_list:
                                template_trigger_id_list.append(str(trigger_obj.id))
                            alert_counter_data = json.loads(REDIS_OBJ.get(alert_counter_redis_key).decode())
                            # 删除报警计数中相关数据，key->action_id,value->{\"CentOS-03_172.16.99.25\": {\"3\": {\"last_alert\": 1528083651.9851427, \"counter\": 1}}}
                            for key1, value1 in alert_counter_data.items():
                                # key->hostname,value->{\"3\": {\"last_alert\": 1528083651.9851427, \"counter\": 1}}
                                for key2, value2 in value1.items():
                                    if host_obj.hostname == key2:   # hostname匹配上了
                                        # key->trigger_id,value->{\"last_alert\": 1528083651.9851427, \"counter\": 1}
                                        for key3 in list(value2.keys()):
                                            if key3 in template_trigger_id_list:
                                                del alert_counter_data[key1][key2][key3]    # 删除对应主机下的trigger计数
                    host_group_obj.delete()
                    Logger().log(message='删除主机组成功,%s' % host_group_obj.name, mode=True)
            response.message = '删除主机组成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除主机组失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
