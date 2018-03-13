from django.shortcuts import render
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@monitor_api_auth
def client_configs(request):
    """客户端向api提交申请并返回数据"""
    pass
