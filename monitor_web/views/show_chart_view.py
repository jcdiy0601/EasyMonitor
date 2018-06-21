#!/usr/bin/env python
# Author: 'JiaChen'

import json
import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from monitor_data import models
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn

REDIS_OBJ = redis_conn(settings)


@login_required
def show_chart(request):
    """图形视图"""
    host_group_obj_list = models.HostGroup.objects.all()
    host_obj_list = models.Host.objects.all()
    return render(request, 'show_chart.html', {'host_group_obj_list': host_group_obj_list,
                                               'host_obj_list': host_obj_list})


@login_required
def select_host_group_for_show_chart(request):
    """选择主机组"""
    if request.method == 'POST':
        response = WebResponse()
        host_group_id = request.POST.get('host_group_id')
        host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
        data = list(host_group_obj.host_set.all().values('id', 'ip'))
        response.data = data
        return JsonResponse(response.__dict__)


@login_required
def select_host_for_show_chart(request):
    """选择主机"""
    if request.method == 'POST':
        response = WebResponse()
        host_id = request.POST.get('host_id')
        host_group_id = request.POST.get('host_group_id')
        host_obj = models.Host.objects.filter(id=host_id).first()
        host_group_obj = models.HostGroup.objects.filter(id=host_group_id).first()
        template_obj_list = list(host_obj.templates.all())
        if host_group_obj:
            for item in list(host_group_obj.templates.all()):
                if item not in template_obj_list:
                    template_obj_list.append(item)
        chart_list = []
        # [{'id': 1, 'name': 'CPU负载'}, {'id': 2, 'name': '硬盘空间使用'}, {'id': 3, 'name': '网络流量'}]
        for template_obj in template_obj_list:
            for chart_obj in template_obj.chart_set.all():
                if chart_obj.auto:  # 自动需要获取redis
                    redis_key_name = 'Data_%s_%s_latest' % (host_obj.hostname, chart_obj.applications.name)
                    last_point = json.loads(REDIS_OBJ.lrange(redis_key_name, -1, -1)[-1].decode())
                    # [{'data': {'ens33': {'t_in': 0.28, 't_out': 0.1}, 'lo': {'t_in': 0.0, 't_out': 0.0}}}, 1529472380.8842905]
                    name_list = []
                    for k1, v1 in last_point[0].items():
                        if k1 == 'data':
                            for k2, v2 in v1.items():
                                name_list.append(k2)
                    for name in name_list:
                        chart_list.append({'id': chart_obj.id, 'name': '%s %s' % (chart_obj.name, name)})
                else:
                    chart_list.append({'id': chart_obj.id, 'name': chart_obj.name})
        response.data = chart_list
        return JsonResponse(response.__dict__)


@login_required
def select_chart_for_show_chart(request):
    """选择图表"""
    if request.method == 'POST':
        response = WebResponse()
        data = {'chart_name': None,
                'chart_type': None,
                'chart_data': None,
                'chart_data_unit': None}
        chart_id = request.POST.get('chart_id')
        chart_name = request.POST.get('chart_name')
        if len(chart_name.split()) == 2:
            special_key = chart_name.split()[-1]
        else:
            special_key = None
        search_time = int(request.POST.get('search_time'))
        host_id = request.POST.get('host_id')
        chart_obj = models.Chart.objects.filter(id=chart_id).first()
        host_obj = models.Host.objects.filter(id=host_id).first()
        if special_key:
            data['chart_name'] = '%s %s' % (chart_obj.name, special_key)
        else:
            data['chart_name'] = chart_obj.name
        data['chart_type'] = chart_obj.chart_type
        chart_data_unit = chart_obj.items.all().first().data_unit
        data['chart_data_unit'] = chart_data_unit
        if search_time <= 604800:
            time_tag = 'latest'
        elif 604800 < search_time <= 2592000:
            time_tag = '10min'
        elif 2592000 < search_time <= 7776000:
            time_tag = '30min'
        else:
            time_tag = '1hour'
        application_obj = chart_obj.applications
        redis_key_name = 'Data_%s_%s_%s' % (host_obj.hostname, application_obj.name, time_tag)
        item_obj_list = chart_obj.items.all()
        item_name_list = []
        for item_obj in item_obj_list:
            item_name_list.append(item_obj.key)
        approximate_data_point = int((search_time + 60) / application_obj.interval)
        approximate_data_list = [
            json.loads(i.decode()) for i in REDIS_OBJ.lrange(
                redis_key_name, -approximate_data_point, -1
            )
        ]
        data_list = []
        for point in approximate_data_list:
            value_dict, save_time = point
            if time.time() - save_time < search_time:
                data_list.append(point)
        # data: [[1529396379937.173, 2.11]] 最后数据
        # 无data redis数据 [[{'load5': 0.01, 'load1': 0.0, 'load15': 0.05}, 1529474049.0319276], [{'load5': 0.01, 'load1': 0.0, 'load15': 0.05}, 1529474108.3643043]]
        # 有data redis数据 [[{'data': {'/': {'Size': 48097, 'Used': 2034, 'Avail': 46063, 'Use': 5}, '/boot': {'Size': 1014, 'Used': 155, 'Avail': 860, 'Use': 16}}}, 1529474108.3532693]]
        chart_data = []
        if data_list:
            last_point = data_list[-1][0]
        else:
            last_point = None
        if last_point:
            if 'data' in last_point:    # 有data
                if chart_obj.chart_type == 'line' or chart_obj.chart_type == 'area':    # 线型图或面积图
                    for item_name in item_name_list:
                        chart_data.append({'name': item_name, 'data': []})
                    for data_point in data_list:
                        data_dict = data_point[0]   # {'data': {'lo': {'t_out': 0.0, 't_in': 0.0}, 'ens33': {'t_out': 0.07, 't_in': 0.17}}
                        save_time = data_point[1]
                        for k1, v1 in data_dict['data'].items():
                            if k1 == special_key:    # 字段对上了
                                for k2, v2 in v1.items():
                                    temp_list = []
                                    temp_list.append(save_time * 1000)
                                    temp_list.append(v2)
                                    for item in chart_data:
                                        if item['name'] == k2:
                                            item['data'].append(temp_list)
                else:   # 饼图
                    # {'data': {'/boot': {'Use': 16, 'Avail': 860, 'Used': 155, 'Size': 1014}, '/': {'Use': 5, 'Avail': 46055, 'Used': 2043, 'Size': 48097}}}
                    for k, v in last_point['data'].items():
                        if k == special_key:    # 对上了
                            key = item_name_list[0]
                            # [{'data': 5, 'name': '已使用'}]
                            chart_data.append({'name': '已使用', 'data': v[key]})
            else:   # 无data
                if time_tag == 'latest':    # 无优化值
                    if chart_obj.chart_type == 'line' or chart_obj.chart_type == 'area':    # 线型图或面积图
                        for item_name in item_name_list:
                            chart_data.append({'name': item_name, 'data': []})
                        for data_point in data_list:
                            data_dict = data_point[0]
                            save_time = data_point[1]
                            for k, v in data_dict.items():
                                temp_list = []
                                temp_list.append(save_time*1000)
                                temp_list.append(v)
                                for item in chart_data:
                                    if item['name'] == k:
                                        item['data'].append(temp_list)
                    else:   # 饼图
                        pass
                else:   # 优化值
                    if chart_obj.chart_type == 'line' or chart_obj.chart_type == 'area':    # 线型图或面积图
                        for item_name in item_name_list:
                            chart_data.append({'name': item_name, 'data': []})
                        for data_point in data_list:
                            data_dict = data_point[0]
                            save_time = data_point[1]
                            if data_dict is not None:
                                for k, v in data_dict.items():
                                    temp_list = []
                                    temp_list.append(save_time * 1000)
                                    if special_key:
                                        if special_key == k:
                                            for item_key, item_value in v.items():
                                                for item in chart_data:
                                                    if item['name'] == item_key:
                                                        temp_list.append(item_value[0])
                                                        item['data'].append(temp_list)
                                    else:
                                        temp_list.append(v[0])
                                        for item in chart_data:
                                            if item['name'] == k:
                                                item['data'].append(temp_list)
        data['chart_data'] = chart_data
        response.data = data
        return JsonResponse(response.__dict__)
