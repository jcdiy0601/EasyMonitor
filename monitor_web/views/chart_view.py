#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import chart_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.permissions import check_permission


@login_required
@check_permission
def chart(request):
    """图表视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    chart_obj_list = models.Chart.objects.all()
    chart_obj_count = chart_obj_list.count()
    page_obj = Page(current_page, chart_obj_count)
    chart_obj_list = chart_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('chart.html')
    return render(request, 'chart.html', {'chart_obj_list': chart_obj_list, 'page_str': page_str})


@login_required
@check_permission
def add_chart(request):
    """创建图表视图"""
    if request.method == 'GET':
        form_obj = chart_form.AddChartForm()
        return render(request, 'add_chart.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = chart_form.AddChartForm(request.POST)
        if form_obj.is_valid():
            item_id_list = form_obj.cleaned_data.pop('item_id')
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    chart_obj = models.Chart.objects.create(**data)
                    chart_obj.items.add(*item_id_list)
                Logger().log(message='创建图表成功,%s' % chart_obj.name, mode=True)
                return redirect('/monitor_web/chart.html')
            except Exception as e:
                Logger().log(message='创建图表失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加图表失败'), code='invalid')
        else:
            return render(request, 'add_chart.html', {'form_obj': form_obj})


# @login_required
# @check_permission
# def edit_chart(request, *args, **kwargs):
#     """编辑图表视图"""
#     cid = kwargs['cid']
#     if request.method == 'GET':
#         form_obj = chart_form.EditChartForm(initial={'cid': cid})
#         return render(request, 'edit_chart.html', {'form_obj': form_obj, 'cid': cid})
#     elif request.method == 'POST':
#         form_obj = chart_form.EditChartForm(request.POST, initial={'cid': cid})
#         if form_obj.is_valid():
#             item_id_list = form_obj.cleaned_data.pop('item_id')
#             data = form_obj.cleaned_data
#             try:
#                 with transaction.atomic():
#                     chart_obj = models.Chart.objects.filter(id=cid).first()
#                     models.Chart.objects.filter(id=cid).update(**data)
#                     chart_obj.items.set(item_id_list)
#                 Logger().log(message='修改图表成功,%s' % chart_obj.name, mode=True)
#                 return redirect('/monitor_web/chart.html')
#             except Exception as e:
#                 Logger().log(message='修改图表失败,%s' % str(e), mode=False)
#                 raise ValidationError(_('修改图表失败'), code='invalid')
#         else:
#             return render(request, 'edit_chart.html', {'form_obj': form_obj, 'cid': cid})


@login_required
@check_permission
def del_chart(request):
    """删除图表视图"""
    if request.method == 'POST':
        response = WebResponse()
        chart_list = request.POST.getlist('chart_list')
        try:
            with transaction.atomic():
                for chart_id in chart_list:
                    chart_id = int(chart_id)
                    chart_obj = models.Chart.objects.filter(id=chart_id).first()
                    chart_obj.delete()
                    Logger().log(message='删除图表成功,%s' % chart_obj.name, mode=True)
            response.message = '删除图表成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除图表失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)


@login_required
def get_application(request):
    if request.method == 'POST':
        response = WebResponse()
        template_id = request.POST.get('template_id')
        template_obj = models.Template.objects.filter(id=template_id).first()
        data = list(template_obj.applications.all().values('id', 'name'))
        response.data = data
        return JsonResponse(response.__dict__)


@login_required
def get_item(request):
    if request.method == 'POST':
        response = WebResponse()
        application_id = request.POST.get('application_id')
        application_obj = models.Application.objects.filter(id=application_id).first()
        data = list(application_obj.items.all().values('id', 'name', 'key'))
        response.data = data
        return JsonResponse(response.__dict__)
