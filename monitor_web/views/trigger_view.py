#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import application_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse


@login_required
def trigger(request):
    """应用集视图"""
    template_id = request.GET.get('templateid')
    if template_id:
        template_id = int(template_id)
    else:
        template_id = 0
    template_obj_list = models.Template.objects.all()
    template_obj = models.Template.objects.filter(id=template_id).first()
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    if template_obj:
        application_obj_list = template_obj.applications.all()
        application_obj_count = application_obj_list.count()
        page_obj = Page(current_page, application_obj_count)
        application_obj_list = application_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='application.html', template_id=template_id)
    else:
        application_obj_list = models.Application.objects.all()
        application_obj_count = application_obj_list.count()
        page_obj = Page(current_page, application_obj_count)
        application_obj_list = application_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='application.html', template_id=template_id)
    return render(request, 'application.html', {'application_obj_list': application_obj_list,
                                                'page_str': page_str,
                                                'template_obj_list': template_obj_list,
                                                'template_id': template_id})


@login_required
def add_trigger(request):
    """创建应用集视图"""
    if request.method == 'GET':
        form_obj = application_form.AddApplicationForm()
        return render(request, 'add_application.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = application_form.AddApplicationForm(request.POST)
        if form_obj.is_valid():
            item_id_list = form_obj.cleaned_data.pop('item_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    application_obj = models.Application.objects.create(**data)
                    application_obj.items.add(*item_id_list)
                Logger().log(message='创建应用集成功,%s' % application_obj.name, mode=True)
                return redirect('/monitor_web/application.html')
            except Exception as e:
                Logger().log(message='创建应用集失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加应用集失败'), code='invalid')
        else:
            return render(request, 'add_application.html', {'form_obj': form_obj})


@login_required
def edit_trigger(request, *args, **kwargs):
    """编辑应用集视图"""
    aid = kwargs['aid']
    if request.method == 'GET':
        form_obj = application_form.EditApplicationForm(initial={'aid': aid})
        return render(request, 'edit_application.html', {'form_obj': form_obj, 'aid': aid})
    elif request.method == 'POST':
        form_obj = application_form.EditApplicationForm(request.POST, initial={'aid': aid})
        if form_obj.is_valid():
            item_id_list = form_obj.cleaned_data.pop('item_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    models.Application.objects.filter(id=aid).update(**data)
                    application_obj = models.Application.objects.filter(id=aid).first()
                    application_obj.items.set(item_id_list)
                Logger().log(message='修改应用集成功,%s' % application_obj.name, mode=True)
                return redirect('/monitor_web/application.html')
            except Exception as e:
                Logger().log(message='修改应用集失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改应用集失败'), code='invalid')
        else:
            return render(request, 'edit_application.html', {'form_obj': form_obj, 'aid': aid})


@login_required
def del_trigger(request):
    """删除应用集视图"""
    if request.method == 'POST':
        response = WebResponse()
        application_list = request.POST.getlist('application_list')
        try:
            with transaction.atomic():
                for application_id in application_list:
                    application_id = int(application_id)
                    application_obj = models.Application.objects.filter(id=application_id).first()
                    application_obj.delete()
                    Logger().log(message='删除应用集成功,%s' % application_obj.name, mode=True)
            response.message = '删除应用集成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除应用集失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)
