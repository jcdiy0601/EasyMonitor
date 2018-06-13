#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import item_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.permissions import check_permission


@login_required
@check_permission
def item(request):
    """监控项视图"""
    application_id = request.GET.get('applicationid')
    if application_id:
        application_id = int(application_id)
    else:
        application_id = 0
    application_obj_list = models.Application.objects.all()
    application_obj = models.Application.objects.filter(id=application_id).first()
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    if application_obj:
        item_obj_list = application_obj.items.all()
        item_obj_count = item_obj_list.count()
        page_obj = Page(current_page, item_obj_count)
        item_obj_list = item_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='item.html', application_id=application_id)
    else:
        item_obj_list = models.Item.objects.all()
        item_obj_count = item_obj_list.count()
        page_obj = Page(current_page, item_obj_count)
        item_obj_list = item_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='item.html', application_id=application_id)
    return render(request, 'item.html', {'item_obj_list': item_obj_list,
                                         'page_str': page_str,
                                         'application_obj_list': application_obj_list,
                                         'application_id': application_id})


@login_required
@check_permission
def add_item(request):
    """创建监控项视图"""
    if request.method == 'GET':
        form_obj = item_form.AddItemForm()
        return render(request, 'add_item.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = item_form.AddItemForm(request.POST)
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    item_obj = models.Item.objects.create(**data)
                Logger().log(message='创建监控项成功,%s' % item_obj.key, mode=True)
                return redirect('/monitor_web/item.html')
            except Exception as e:
                Logger().log(message='创建监控项失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加监控项失败'), code='invalid')
        else:
            return render(request, 'add_item.html', {'form_obj': form_obj})


@login_required
@check_permission
def edit_item(request, *args, **kwargs):
    """编辑监控项视图"""
    iid = kwargs['iid']
    if request.method == 'GET':
        form_obj = item_form.EditItemForm(initial={'iid': iid})
        return render(request, 'edit_item.html', {'form_obj': form_obj, 'iid': iid})
    elif request.method == 'POST':
        form_obj = item_form.EditItemForm(request.POST, initial={'iid': iid})
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    item_obj = models.Item.objects.filter(id=iid).first()
                    models.Item.objects.filter(id=iid).update(**data)
                Logger().log(message='修改监控项成功,%s' % item_obj.key, mode=True)
                return redirect('/monitor_web/item.html')
            except Exception as e:
                Logger().log(message='修改监控项失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改监控项失败'), code='invalid')
        else:
            return render(request, 'edit_item.html', {'form_obj': form_obj, 'iid': iid})


@login_required
@check_permission
def del_item(request):
    """删除监控项视图"""
    if request.method == 'POST':
        response = WebResponse()
        item_list = request.POST.getlist('item_list')
        try:
            with transaction.atomic():
                for item_id in item_list:
                    item_id = int(item_id)
                    item_obj = models.Item.objects.filter(id=item_id).first()
                    item_obj.delete()
                    Logger().log(message='删除监控项成功,%s' % item_obj.key, mode=True)
            response.message = '删除监控项成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除监控项失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
