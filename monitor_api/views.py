from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt
import json
from utils.get_client_config import ClientHandle
from utils.redis_conn import redis_conn
from django.conf import settings
from utils.data_optimization import DataStore
from monitor_data import models
from utils.serializer import get_application_trigger
from utils.data_processing import DataHandler
from utils.log import Logger

REDIS_OBJ = redis_conn(settings)


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
            hostname = report_data['hostname']
            application_name = report_data['application_name']
            data = report_data['data']
            host_obj = models.Host.objects.filter(hostname=hostname).first()
            if not host_obj:
                response['code'] = 404
                response['message'] = '资源不存在,%s' % hostname
                Logger().log(message='资源不存在,%s' % hostname, mode=False)
            data_save_obj = DataStore(hostname, application_name, data, REDIS_OBJ, response)  # 对客户端汇报上来的数据进行优化存储
            response = data_save_obj.response  # 回复客户端，至此与客户端交互操作完成
            # 触发器检测
            application_trigger_list = get_application_trigger(application_name)    # 获取应用集对应触发器列表
            trigger_handler = DataHandler(connect_redis=False)
            for application_trigger_obj in application_trigger_list:    # 循环每个触发器
                trigger_handler.load_application_data_and_calulating(host_obj, application_trigger_obj, REDIS_OBJ)  # 加载应用集数据并计算
        except Exception as e:
            response['code'] = 500
            response['message'] = '服务器错误,%s' % str(e)
            Logger().log(message='%s' % str(e), mode=False)
        return JsonResponse(data=response, json_dumps_params={'ensure_ascii': False})
