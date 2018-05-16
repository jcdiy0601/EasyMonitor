import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from EasyMonitor import forms
from monitor_data import models
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn

REDIS_OBJ = redis_conn(settings)


def acclogin(request):
    """用户登录视图"""
    if request.method == 'POST':
        form_obj = forms.AccloginForm(request.POST)  # 表单认证
        if form_obj.is_valid():  # 表单验证成功
            user = authenticate(**form_obj.cleaned_data)  # 用户认证
            if user:  # 用户认证成功
                if user.is_active:  # 用户具有登录权限
                    login(request, user)
                    return redirect('/')
                else:
                    error_message = '该邮箱无权登录'
            else:
                error_message = '用户认证失败,邮箱或密码错误'
        else:
            error_message = '邮箱或密码不能为空'  # 这里格式不对在浏览器提交前就会提示，所以只有空这种可能
        return render(request, 'acclogin.html', {'form_obj': form_obj, 'error_message': error_message})
    form_obj = forms.AccloginForm()
    return render(request, 'acclogin.html', {'form_obj': form_obj})


def acclogout(request):
    """用户登出视图"""
    logout(request)
    return redirect('/login.html')


@login_required
def index(request):
    """首页视图"""
    host_info_dict = {'count': models.Host.objects.all().count(),
                      'online': models.Host.objects.filter(status=1).count(),
                      'problem': models.Host.objects.filter(status=5).count(),
                      'other': models.Host.objects.exclude(status__in=[1, 5]).count()}
    trigger_info_dict = {'count': models.Trigger.objects.all().count(),
                         'enabled': models.Trigger.objects.filter(enabled=True).count(),
                         'disabled': models.Trigger.objects.filter(enabled=False).count()}
    action_info_dict = {'count': models.Action.objects.all().count(),
                        'enabled': models.Action.objects.filter(enabled=True).count(),
                        'disabled': models.Action.objects.filter(enabled=False).count()}
    host_group_obj_list = models.HostGroup.objects.all()
    host_group_info_dict = {}
    for host_group_obj in host_group_obj_list:
        host_group_info_dict[host_group_obj.name] = {'disaster': 0,
                                                     'high': 0,
                                                     'general': 0,
                                                     'warning': 0,
                                                     'information': 0,
                                                     'problem': 0,
                                                     'no_problem': 0}
        host_obj_list = set(host_group_obj.host_set.all())
        for host_obj in host_obj_list:
            trigger_key_in_redis = 'host_%s_trigger*' % host_obj.hostname
            key_list = REDIS_OBJ.keys(trigger_key_in_redis)
            if key_list:
                host_group_info_dict[host_group_obj.name]['problem'] += 1
            else:
                host_group_info_dict[host_group_obj.name]['no_problem'] += 1
            for key in key_list:
                trigger_id = key.decode().split('_')[-1]
                trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()
                trigger_severity = trigger_obj.severity
                host_group_info_dict[host_group_obj.name][trigger_severity] += 1
    return render(request, 'index.html', {'host_info_dict': host_info_dict,
                                          'trigger_info_dict': trigger_info_dict,
                                          'action_info_dict': action_info_dict,
                                          'host_group_info_dict': host_group_info_dict})


@login_required
def user_info(request):
    """用户信息视图"""
    if request.method == 'POST':
        response = WebResponse()
        form_obj = forms.UserInfoForm(request.POST)
        if form_obj.is_valid():
            password = form_obj.cleaned_data['password1']
            request.user.set_password(password)
            request.user.save()
        else:
            response.status = False
            response.message = '密码修改失败'
        return JsonResponse(response.__dict__)
    return render(request, 'user_info.html')
