#!/usr/bin/env python
# Author: 'JiaChen'


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import host_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse


@login_required
def host(request):
    """主机组视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    host_obj_list = models.Host.objects.all()
    host_obj_count = host_obj_list.count()
    page_obj = Page(current_page, host_obj_count)
    host_obj_list = host_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('host.html')
    return render(request, 'host.html', {'host_obj_list': host_obj_list, 'page_str': page_str})


@login_required
def add_host(request):
    """创建主机视图"""
    if request.method == 'GET':
        form_obj = host_form.AddHostForm()
        return render(request, 'add_host.html', {'form_obj': form_obj})
