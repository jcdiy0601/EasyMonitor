#!/usr/bin/env python
# Author: 'JiaChen'

import time
import hashlib
from django.http import JsonResponse
from django.conf import settings
from utils.log import Logger

ENCRYPT_LIST = []  # {'encrypt': encrypt, 'time': timestamp}


def monitor_api_auth_method(request):
    """api认证，成功返回True，错误返回False"""
    auth_key = request.META.get(settings.MONITOR_AUTH_HEADER_NAME)  # f73c8691e6c932f2063652796cb49186|1512458859.455036
    if not auth_key:  # 如果没有接收到认证key，则返回False
        return False
    temp_list = auth_key.split('|')
    if len(temp_list) != 2:  # 如果临时列表不等于2个内容，则返回False
        return False
    encrypt, timestamp = temp_list
    timestamp = float(timestamp)
    limit_timestamp = time.time() - settings.MONITOR_AUTH_TIME  # 临界超时时间
    if limit_timestamp > timestamp:  # 访问超时了
        return False
    ha = hashlib.md5(settings.MONITOR_AUTH_KEY.encode('utf-8'))
    ha.update(bytes('%s|%f' % (settings.MONITOR_AUTH_KEY, timestamp), encoding='utf-8'))
    result = ha.hexdigest()
    if encrypt != result:  # 认证加密串不同
        return False
    exist = False
    del_keys = []
    for k, v in enumerate(ENCRYPT_LIST):
        m = v['time']
        n = v['encrypt']
        if m < limit_timestamp:  # 之前记录的时间小于最大超时时间
            del_keys.append(k)
            continue
        if n == encrypt:  # 新的加密内容"|"前面部分与之前记录相同
            exist = True
    del_keys = sorted(del_keys, reverse=True)
    for k in del_keys:
        del ENCRYPT_LIST[k]
    if exist:  # 如果存在说明加密串被截获，则返回False
        return False
    ENCRYPT_LIST.append({'encrypt': encrypt, 'time': timestamp})
    return True


def monitor_api_auth(func):
    """api认证装饰器"""

    def wrapper(request, *args, **kwargs):
        if not monitor_api_auth_method(request):
            Logger().log(message='API认证未通过', mode=False)
            return JsonResponse(data={'code': 401, 'message': 'API认证未通过'}, json_dumps_params={'ensure_ascii': False})
        return func(request, *args, **kwargs)

    return wrapper
