from django.shortcuts import render, HttpResponse
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt
import json
from utils.get_client_config import ClientHandle


@csrf_exempt
@monitor_api_auth
def client_configs(request):
    """客户端向api提交申请并返回配置数据"""
    hostname = request.GET.get('hostname')
    config_ojb = ClientHandle(hostname)
    config = config_ojb.fetch_configs()
    print(config, type(config))
    if config:
        return HttpResponse(json.dumps(config))