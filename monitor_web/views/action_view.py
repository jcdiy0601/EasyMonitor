#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import action_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.permissions import check_permission


@login_required
@check_permission
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
@check_permission
def add_action(request):
    """创建报警策略视图"""
    if request.method == 'GET':
        form_obj = action_form.AddActionForm()
        return render(request, 'add_action.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = action_form.AddActionForm(request.POST)
        if form_obj.is_valid():
            trigger_id_list = form_obj.cleaned_data.pop('trigger_id')
            action_operation_id_list = form_obj.cleaned_data.pop('action_operation_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    action_obj = models.Action.objects.create(**data)
                    action_obj.triggers.add(*trigger_id_list)
                    action_obj.action_operations.add(*action_operation_id_list)
                Logger().log(message='创建报警策略成功,%s' % action_obj.name, mode=True)
                return redirect('/monitor_web/action.html')
            except Exception as e:
                Logger().log(message='创建报警策略失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加报警策略失败'), code='invalid')
        else:
            return render(request, 'add_action.html', {'form_obj': form_obj})


@login_required
@check_permission
def edit_action(request, *args, **kwargs):
    """修改报警策略视图"""
    aid = kwargs['aid']
    if request.method == 'GET':
        form_obj = action_form.EditActionForm(initial={'aid': aid})
        return render(request, 'edit_action.html', {'form_obj': form_obj, 'aid': aid})
    elif request.method == 'POST':
        form_obj = action_form.EditActionForm(request.POST, initial={'aid': aid})
        if form_obj.is_valid():
            trigger_id_list = form_obj.cleaned_data.pop('trigger_id')
            action_operation_id_list = form_obj.cleaned_data.pop('action_operation_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.Action.objects.filter(id=aid).update(**data)
                    action_obj = models.Action.objects.filter(id=aid).first()
                    action_obj.triggers.set(trigger_id_list)
                    action_obj.action_operations.set(action_operation_id_list)
                Logger().log(message='修改报警策略成功,%s' % action_obj.name, mode=True)
                return redirect('/monitor_web/action.html')
            except Exception as e:
                Logger().log(message='修改报警策略失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改报警策略失败'), code='invalid')
        else:
            return render(request, 'edit_action.html', {'form_obj': form_obj, 'aid': aid})


@login_required
@check_permission
def del_action(request):
    """删除报警策略视图"""
    if request.method == 'POST':
        response = WebResponse()
        action_list = request.POST.getlist('action_list')
        try:
            with transaction.atomic():
                for action_id in action_list:
                    action_id = int(action_id)
                    action_obj = models.Action.objects.filter(id=action_id).first()
                    action_obj.delete()
                    Logger().log(message='删除报警策略成功,%s' % action_obj.name, mode=True)
            response.message = '删除报警策略成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除报警策略失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
