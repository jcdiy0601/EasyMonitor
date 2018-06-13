#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import action_operation_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.permissions import check_permission


@login_required
@check_permission
def action_operation(request):
    """报警动作视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    action_operation_obj_list = models.ActionOperation.objects.all()
    action_operation_obj_count = action_operation_obj_list.count()
    page_obj = Page(current_page, action_operation_obj_count)
    action_operation_obj_list = action_operation_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('action_operation.html')
    return render(request, 'action_operation.html', {'action_operation_obj_list': action_operation_obj_list,
                                                     'page_str': page_str})


@login_required
@check_permission
def add_action_operation(request):
    """创建报警动作视图"""
    if request.method == 'GET':
        form_obj = action_operation_form.AddActionOperationForm()
        return render(request, 'add_action_operation.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = action_operation_form.AddActionOperationForm(request.POST)
        if form_obj.is_valid():
            user_profile_id_list = form_obj.cleaned_data.pop('user_profile_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    action_operation_obj = models.ActionOperation.objects.create(**data)
                    action_operation_obj.user_profiles.add(*user_profile_id_list)
                Logger().log(message='创建报警策略成功,%s' % action_operation_obj.name, mode=True)
                return redirect('/monitor_web/action_operation.html')
            except Exception as e:
                Logger().log(message='创建报警动作失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加报警动作失败'), code='invalid')
        else:
            return render(request, 'add_action_operation.html', {'form_obj': form_obj})


@login_required
@check_permission
def edit_action_operation(request, *args, **kwargs):
    """修改报警动作视图"""
    aid = kwargs['aid']
    if request.method == 'GET':
        form_obj = action_operation_form.EditActionOperationForm(initial={'aid': aid})
        return render(request, 'edit_action_operation.html', {'form_obj': form_obj, 'aid': aid})
    elif request.method == 'POST':
        form_obj = action_operation_form.EditActionOperationForm(request.POST, initial={'aid': aid})
        if form_obj.is_valid():
            user_profile_id_list = form_obj.cleaned_data.pop('user_profile_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.ActionOperation.objects.filter(id=aid).update(**data)
                    action_operation_obj = models.ActionOperation.objects.filter(id=aid).first()
                    action_operation_obj.user_profiles.set(user_profile_id_list)
                Logger().log(message='修改报警动作成功,%s' % action_operation_obj.name, mode=True)
                return redirect('/monitor_web/action_operation.html')
            except Exception as e:
                Logger().log(message='修改报警动作失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改报警动作失败'), code='invalid')
        else:
            return render(request, 'edit_action_operation.html', {'form_obj': form_obj, 'aid': aid})


@login_required
@check_permission
def del_action_operation(request):
    """删除报警动作视图"""
    if request.method == 'POST':
        response = WebResponse()
        action_operation_list = request.POST.getlist('action_operation_list')
        try:
            with transaction.atomic():
                for action_operation_id in action_operation_list:
                    action_operation_id = int(action_operation_id)
                    action_operation_obj = models.ActionOperation.objects.filter(id=action_operation_id).first()
                    action_operation_obj.delete()
                    Logger().log(message='删除报警动作成功,%s' % action_operation_obj.name, mode=True)
            response.message = '删除报警动作成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除报警动作失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
