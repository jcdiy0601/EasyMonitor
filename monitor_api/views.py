from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt
import json
from utils.get_client_config import GetClientConfigHandle
from utils.redis_conn import redis_conn
from django.conf import settings
from utils.data_store_optimization import DataStoreOptimizationHandle
from monitor_data import models
from utils.serializer import get_application_trigger
from utils.data_processing import DataHandler
from utils.log import Logger
from utils.data_verification import DataVerificationHandle
from utils.api_response import ApiResponse

REDIS_OBJ = redis_conn(settings)


@monitor_api_auth
def client_config(request):
    """客户端向api提交申请并返回配置数据"""
    hostname = request.GET.get('hostname')
    get_client_config_handle_ojb = GetClientConfigHandle(hostname)
    client_config_dict = get_client_config_handle_ojb.fetch_config()
    '''
    {'application': {'LinuxLoad': ['LinuxLoadPlugin', 60], 'LinuxDisk': ['LinuxDiskP
    lugin', 60], 'LinuxNetwork': ['LinuxNetworkPlugin', 60], 'LinuxMemory': ['LinuxM
    emoryPlugin', 30], 'LinuxCpu': ['LinuxCpuPlugin', 30]}, 'code': 200, 'message':
    '获取监控配置成功'}
    '''
    return JsonResponse(client_config_dict)


@csrf_exempt
@monitor_api_auth
def client_data(request):
    """客户端向api提交监控数据"""
    response = ApiResponse().response
    if request.method == 'POST':
        try:
            client_report_data_dict = json.loads(request.body.decode('utf-8'))  # 获取客户端汇报数据字典
            hostname = client_report_data_dict.get('hostname', None)  # 获取主机名
            application_name = client_report_data_dict.get('application_name', None)  # 获取应用集名称
            data = client_report_data_dict.get('data', None)  # 获取监控数据
            data_verification_obj = DataVerificationHandle(response=response, hostname=hostname, application_name=application_name, data=data)
            response, data = data_verification_obj.check_data()
            if not data:    # 无效数据或基础信息有误
                return JsonResponse(response)
            else:   # 有效数据
                print(data)
                data_store_optimization_obj = DataStoreOptimizationHandle(hostname=hostname,
                                                                          application_name=application_name,
                                                                          data=data,
                                                                          redis_obj=REDIS_OBJ)  # 对客户端汇报上来的数据进行优化存储


            # 触发器检测
            # application_trigger_list = get_application_trigger(application_name)    # 获取应用集对应触发器列表
            # trigger_handler = DataHandler(connect_redis=False)
            # for application_trigger_obj in application_trigger_list:    # 循环每个触发器
            #     trigger_handler.load_application_data_and_calulating(host_obj, application_trigger_obj, REDIS_OBJ)  # 加载应用集数据并计算
        except Exception as e:
            response['code'] = 500
            response['message'] = '服务器错误,%s' % str(e)
            Logger().log(message='服务器错误,%s' % str(e), mode=False)
        return JsonResponse(response)
