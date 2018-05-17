#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from monitor_data import models
from monitor_web.forms import host_group_form
from utils.pagination import Page
from utils.log import Logger


@login_required
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
def add_host_group(request):
    """主机组添加视图"""
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
                    host_group_obj.templates.add(template_id_list)
                Logger().log(message='创建主机组成功,%s' % host_group_obj.name, mode=True)
                return redirect('/monitor_web/host_group.html')
            except Exception as e:
                Logger().log(message='创建主机组失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加主机组失败'), code='invalid')
        else:
            return render(request, 'add_host_group.html', {'form_obj': form_obj})


@login_required
def edit_host_group(request, *args, **kwargs):
    """主机组删除视图"""
    hid = kwargs['hid']
    if request.method == 'GET':
        form_obj = host_group_form.EditHostGroupForm(initial={'hid': hid})
        return render(request, 'edit_host_group.html', {'form_obj': form_obj, 'hid': hid})
    elif request.method == 'POST':
        form_obj = host_group_form.EditHostGroupForm(request.POST, initial={'hid': hid})
        if form_obj.is_valid():
            template_id_list = form_obj.cleaned_data.pop('template_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.HostGroup.objects.filter(id=hid).update(**data)
                    host_group_obj = models.HostGroup.objects.filter(id=hid).first()
                    host_group_obj.templates.set(template_id_list)
                Logger().log(message='修改主机组成功,%s' % host_group_obj.name, mode=True)
                return redirect('/monitor_web/host_group.html')
            except Exception as e:
                Logger().log(message='修改主机组失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改主机组失败'), code='invalid')
        else:
            return render(request, 'edit_host_group.html', {'form_obj': form_obj, 'hid': hid})


@login_required
def del_host_group(request):
    """主机组删除视图"""
    pass


