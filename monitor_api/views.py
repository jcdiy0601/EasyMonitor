from django.http import JsonResponse
from utils.monitor_api_auth import monitor_api_auth
from django.views.decorators.csrf import csrf_exempt
import json
from utils.get_client_config import GetClientConfigHandle
from utils.redis_conn import redis_conn
from django.conf import settings
from utils.data_store_optimization import DataStoreOptimizationHandle
from monitor_data import models
from utils.serializer import get_application_trigger_obj_set
from utils.data_processing import DataHandle
from utils.log import Logger
from utils.data_verification import DataVerificationHandle
from utils.api_response import ApiResponse

REDIS_OBJ = redis_conn(settings)


@monitor_api_auth
def client_config(request):
    """客户端向api提交申请并返回配置数据"""
    hostname = request.GET.get('hostname')
    response = ApiResponse()
    get_client_config_handle_obj = GetClientConfigHandle(hostname, response.__dict__)
    client_config_dict = get_client_config_handle_obj.fetch_config()
    return JsonResponse(client_config_dict)


@csrf_exempt
@monitor_api_auth
def client_data(request):
    """客户端向api提交监控数据"""
    response = ApiResponse()
    if request.method == 'POST':
        try:
            client_report_data_dict = json.loads(request.body.decode('utf-8'))  # 获取客户端汇报数据字典
            hostname = client_report_data_dict.get('hostname', None)  # 获取主机名
            application_name = client_report_data_dict.get('application_name', None)  # 获取应用集名称
            data = client_report_data_dict.get('data', None)  # 获取监控数据
            data_verification_obj = DataVerificationHandle(response=response.__dict__, hostname=hostname, application_name=application_name, data=data)
            response, data = data_verification_obj.check_data()     # 检查数据返回响应及数据，检查成功data有数据，失败data为None
            if not data:    # 无效数据或基础信息有误
                return JsonResponse(response)
            else:   # 有效数据
                data_store_optimization_obj = DataStoreOptimizationHandle(hostname=hostname,
                                                                          application_name=application_name,
                                                                          data=data,
                                                                          redis_obj=REDIS_OBJ)  # 对客户端汇报上来的数据进行优化存储
                data_store_optimization_obj.process_and_save()  # 数据处理及存储
            # 触发器检测
            trigger_obj_set = get_application_trigger_obj_set(application_name=application_name)   # 获取应用集对应触发器集合
            '''
            {<Trigger: 磁盘IO过高>, <Trigger: cpu使用率过高>}
            '''
            data_handle_obj = DataHandle(connect_redis=False)   # 实例化数据处理
            host_obj = models.Host.objects.filter(hostname=hostname).first()
            for trigger_obj in trigger_obj_set:    # 循环每个触发器
                data_handle_obj.load_application_data_and_calculating(host_obj=host_obj,
                                                                      trigger_obj=trigger_obj,
                                                                      redis_obj=REDIS_OBJ)  # 加载应用集数据并计算
        except Exception as e:
            response['code'] = 500
            response['message'] = '服务器错误,%s' % str(e)
            Logger().log(message='服务器错误,%s' % str(e), mode=False)
        return JsonResponse(response)
