from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt
import json
from utils.get_client_config import ClientHandle


@csrf_exempt
@monitor_api_auth
def client_config(request):
    """客户端向api提交申请并返回配置数据"""
    hostname = request.GET.get('hostname')
    config_ojb = ClientHandle(hostname)
    config = config_ojb.fetch_configs()
    return JsonResponse(data=config, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@monitor_api_auth
def client_data(request):
    """客户端向api提交监控数据"""
    response = {'code': None, 'message': None}
    if request.method == 'POST':
        try:
            report_data = json.loads(request.body.decode('utf-8'))
            report_data = json.loads(report_data)
            print('report_data--------->', report_data, type(report_data))
            hostname = report_data['hostname']
            application_name = report_data['application_name']
            data = report_data['data']
            print('data---------->', type(data))
        except Exception as e:
            pass
    return JsonResponse(response)
