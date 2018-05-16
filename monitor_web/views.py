from django.shortcuts import render
from monitor_data import models


def host_group(request):
    """主机组视图"""
    host_group_obj_list = models.HostGroup.objects.all()
    return render(request, 'user_group.html', {'host_group_obj_list': host_group_obj_list})


def host_group_add(request):
    """主机组添加视图"""
    return render(request, 'user_group_add.html')


def host_group_del(request):
    """主机组删除视图"""
    pass
