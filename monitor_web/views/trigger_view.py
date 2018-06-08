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
from monitor_web.forms import trigger_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn

REDIS_OBJ = redis_conn(settings)


@login_required
def trigger(request):
    """触发器视图"""
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
        trigger_obj_list = template_obj.trigger_set.all()
        trigger_obj_count = trigger_obj_list.count()
        page_obj = Page(current_page, trigger_obj_count)
        trigger_obj_list = trigger_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='trigger.html', template_id=template_id)
    else:
        trigger_obj_list = models.Trigger.objects.all()
        trigger_obj_count = trigger_obj_list.count()
        page_obj = Page(current_page, trigger_obj_count)
        trigger_obj_list = trigger_obj_list[page_obj.start:page_obj.end]
        page_str = page_obj.pager(base_url='trigger.html', template_id=template_id)
    return render(request, 'trigger.html', {'trigger_obj_list': trigger_obj_list,
                                            'page_str': page_str,
                                            'template_obj_list': template_obj_list,
                                            'template_id': template_id})


@login_required
def add_trigger(request):
    """创建触发器视图"""
    if request.method == 'GET':
        form_obj = trigger_form.AddTriggerForm()
        return render(request, 'add_trigger.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        applications_id_list = request.POST.getlist('applications_id')
        items_id_list = request.POST.getlist('items_id')
        specified_item_key_list = request.POST.getlist('specified_item_key')
        operator_list = request.POST.getlist('operator')
        threshold_list = request.POST.getlist('threshold')
        logic_with_next_list = request.POST.getlist('logic_with_next')
        data_calc_func_list = request.POST.getlist('data_calc_func')
        data_calc_func_args_list = request.POST.getlist('data_calc_func_args')
        count = 0
        while count < len(applications_id_list):
            if applications_id_list[count] == '' and items_id_list[count] == '' and operator_list[count] == '':
                applications_id_list.pop(count)
                items_id_list.pop(count)
                specified_item_key_list.pop(count)
                operator_list.pop(count)
                threshold_list.pop(count)
                logic_with_next_list.pop(count)
                data_calc_func_list.pop(count)
                data_calc_func_args_list.pop(count)
                if count == 0:
                    pass
                else:
                    count -= 1
            else:
                count += 1
        trigger_data = {'name': request.POST.get('name'),
                        'templates_id': request.POST.get('templates_id'),
                        'severity': request.POST.get('severity'),
                        'enabled': request.POST.get('enabled'),
                        'memo': request.POST.get('memo')}
        form_obj = trigger_form.AddTriggerForm(trigger_data)
        if form_obj.is_valid():
            try:
                with transaction.atomic():
                    trigger_obj = models.Trigger.objects.create(**form_obj.cleaned_data)
                    triggers_id = trigger_obj.id
                    for index in range(len(applications_id_list)):
                        trigger_expression_data = {'triggers_id': triggers_id,
                                                   'applications_id': applications_id_list[index],
                                                   'items_id': items_id_list[index],
                                                   'specified_item_key': specified_item_key_list[index],
                                                   'operator': operator_list[index],
                                                   'threshold': threshold_list[index],
                                                   'logic_with_next': logic_with_next_list[index],
                                                   'data_calc_func': data_calc_func_list[index],
                                                   'data_calc_func_args': data_calc_func_args_list[index]}
                        if trigger_expression_data['threshold'] == '':  # 无阈值
                            if trigger_expression_data['applications_id'] != '' or trigger_expression_data['items_id'] != '':  # 应用集或监控项不为空
                                raise Exception('触发器表达式有误，有应用集或监控项，但无阈值')
                        elif trigger_expression_data['threshold'] != '':  # 有阈值
                            if trigger_expression_data['applications_id'] == '' or trigger_expression_data['items_id'] == '':  # 应用集或监控项为空
                                raise Exception('触发器表达式有误，有阈值，但无对应应用集或监控项')
                            else:
                                if trigger_expression_data['data_calc_func_args'] != '':
                                    json.loads(trigger_expression_data['data_calc_func_args'])
                                if len(applications_id_list) == index + 1:  # 最后一个表达式
                                    if trigger_expression_data['logic_with_next']:
                                        raise Exception('触发器表达式有误，最后一个表达式不能有逻辑关系符号')
                                models.TriggerExpression.objects.create(**trigger_expression_data)
                Logger().log(message='创建触发器成功,%s' % trigger_obj.name, mode=True)
                return redirect('/monitor_web/trigger.html')
            except Exception as e:
                Logger().log(message='创建触发器失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加触发器失败'), code='invalid')
        else:
            return render(request, 'add_trigger.html', {'form_obj': form_obj})


@login_required
def edit_trigger(request, *args, **kwargs):
    """编辑触发器视图"""
    tid = kwargs['tid']
    if request.method == 'GET':
        form_obj = trigger_form.EditTriggerForm(initial={'tid': tid})
        trigger_obj = models.Trigger.objects.filter(id=tid).first()
        trigger_expression_obj_list = list(trigger_obj.triggerexpression_set.all())
        return render(request, 'edit_trigger.html', {'form_obj': form_obj,
                                                     'tid': tid,
                                                     'trigger_expression_obj_list': trigger_expression_obj_list,
                                                     'trigger_obj': trigger_obj})
    elif request.method == 'POST':
        trigger_obj = models.Trigger.objects.filter(id=tid).first()
        trigger_expression_obj_list = list(trigger_obj.triggerexpression_set.all())
        applications_id_list = request.POST.getlist('applications_id')
        items_id_list = request.POST.getlist('items_id')
        specified_item_key_list = request.POST.getlist('specified_item_key')
        operator_list = request.POST.getlist('operator')
        threshold_list = request.POST.getlist('threshold')
        logic_with_next_list = request.POST.getlist('logic_with_next')
        data_calc_func_list = request.POST.getlist('data_calc_func')
        data_calc_func_args_list = request.POST.getlist('data_calc_func_args')
        count = 0
        while count < len(applications_id_list):
            if applications_id_list[count] == '' and items_id_list[count] == '' and operator_list[count] == '':
                applications_id_list.pop(count)
                items_id_list.pop(count)
                specified_item_key_list.pop(count)
                operator_list.pop(count)
                threshold_list.pop(count)
                logic_with_next_list.pop(count)
                data_calc_func_list.pop(count)
                data_calc_func_args_list.pop(count)
                if count == 0:
                    pass
                else:
                    count -= 1
            else:
                count += 1
        trigger_data = {'name': request.POST.get('name'),
                        'templates_id': request.POST.get('templates_id'),
                        'severity': request.POST.get('severity'),
                        'enabled': request.POST.get('enabled'),
                        'memo': request.POST.get('memo')}
        form_obj = trigger_form.EditTriggerForm(trigger_data, initial={'tid': tid})
        if form_obj.is_valid():
            try:
                with transaction.atomic():
                    models.Trigger.objects.filter(id=tid).update(**form_obj.cleaned_data)
                    triggers_id = trigger_obj.id
                    for index in range(len(applications_id_list)):
                        trigger_expression_data = {'triggers_id': triggers_id,
                                                   'applications_id': applications_id_list[index],
                                                   'items_id': items_id_list[index],
                                                   'specified_item_key': specified_item_key_list[index],
                                                   'operator': operator_list[index],
                                                   'threshold': threshold_list[index],
                                                   'logic_with_next': logic_with_next_list[index],
                                                   'data_calc_func': data_calc_func_list[index],
                                                   'data_calc_func_args': data_calc_func_args_list[index]}
                        if trigger_expression_data['threshold'] == '':  # 无阈值
                            if trigger_expression_data['applications_id'] != '' or trigger_expression_data['items_id'] != '':  # 应用集或监控项不为空
                                raise Exception('触发器表达式有误，有应用集或监控项，但无阈值')
                        elif trigger_expression_data['threshold'] != '':  # 有阈值
                            if trigger_expression_data['applications_id'] == '' or trigger_expression_data['items_id'] == '':  # 应用集或监控项为空
                                raise Exception('触发器表达式有误，有阈值，但无对应应用集或监控项')
                            else:
                                if trigger_expression_data['data_calc_func_args'] != '':
                                    json.loads(trigger_expression_data['data_calc_func_args'])

                                if len(applications_id_list) == index + 1:  # 最后一个表达式
                                    if trigger_expression_data['logic_with_next']:
                                        raise Exception('触发器表达式有误，最后一个表达式不能有逻辑关系符号')
                                trigger_obj.triggerexpression_set.all().delete()
                                models.TriggerExpression.objects.create(**trigger_expression_data)
                Logger().log(message='编辑触发器成功,%s' % trigger_obj.name, mode=True)
                return redirect('/monitor_web/trigger.html')
            except Exception as e:
                Logger().log(message='编辑触发器失败,%s' % str(e), mode=False)
                raise ValidationError(_('编辑触发器失败'), code='invalid')
        else:
            return render(request, 'edit_trigger.html', {'form_obj': form_obj,
                                                         'tid': tid,
                                                         'trigger_expression_obj_list': trigger_expression_obj_list,
                                                         'trigger_obj': trigger_obj})


@login_required
def del_trigger(request):
    """删除触发器视图"""
    if request.method == 'POST':
        response = WebResponse()
        trigger_list = request.POST.getlist('trigger_list')
        try:
            with transaction.atomic():
                for trigger_id in trigger_list:
                    trigger_id = int(trigger_id)
                    trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()
                    key_in_redis = '*_trigger_%s' % trigger_obj.id
                    key_list = REDIS_OBJ.keys(key_in_redis)
                    for key in key_list:
                        REDIS_OBJ.delete(key)  # 删除redis中相关监控项
                    alert_counter_redis_key = settings.ALERT_COUNTER_REDIS_KEY
                    alert_counter_data = json.loads(REDIS_OBJ.get(alert_counter_redis_key).decode())
                    for key1, value1 in alert_counter_data.items():
                        for key2, value2 in value1.items():
                            for key3 in list(value2.keys()):
                                if key3 == str(trigger_id):
                                    del alert_counter_data[key1][key2][key3]  # 删除对应主机下的trigger计数
                    trigger_obj.delete()
                    Logger().log(message='删除触发器成功,%s' % trigger_obj.name, mode=True)
            response.message = '删除触发器成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除触发器失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)


@login_required
def select_application(request):
    """选择应用集"""
    if request.method == 'POST':
        response = WebResponse()
        template_id = request.POST.get('template_id')
        template_obj = models.Template.objects.filter(id=template_id).first()
        data = list(template_obj.applications.all().values('id', 'name'))
        response.data = data
        return JsonResponse(response.__dict__)


@login_required
def select_item(request):
    """选择监控项"""
    if request.method == 'POST':
        response = WebResponse()
        application_id = request.POST.get('application_id')
        application_obj = models.Application.objects.filter(id=application_id).first()
        temp_data = list(application_obj.items.all().values('id', 'name', 'key'))
        data = []
        for item in temp_data:
            name = '%s %s' % (item['name'], item['key'])
            data.append({'id': item['id'], 'name': name})
        response.data = data
        return JsonResponse(response.__dict__)
