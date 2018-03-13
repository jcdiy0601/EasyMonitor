from django.shortcuts import render, HttpResponse
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt
import json
from utils.get_client_config import ClientHandler


@csrf_exempt
@monitor_api_auth
def client_configs(request):
    """客户端向api提交申请并返回配置数据"""
    if request.method == 'POST':
        server_info = json.loads(request.body.decode('utf-8'))
        server_info = json.loads(server_info)
        hostname = server_info.get('hostname', None)
        config_obj = ClientHandler(hostname)
        config = config_obj.fetch_configs()
        print('config------->', config)
        if config:
            return HttpResponse(json.dumps(config))
