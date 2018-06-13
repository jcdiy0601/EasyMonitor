#!/usr/bin/env python
# Author: 'JiaChen'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from monitor_data import models
from monitor_web.forms import user_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.permissions import check_permission
from django.contrib.auth.models import Permission


@login_required
@check_permission
def user(request):
    """用户视图"""
    current_page = request.GET.get("p", 1)
    current_page = int(current_page)
    user_obj_list = models.UserProfile.objects.all()
    user_obj_count = user_obj_list.count()
    page_obj = Page(current_page, user_obj_count)
    user_obj_list = user_obj_list[page_obj.start:page_obj.end]
    page_str = page_obj.pager('user.html')
    return render(request, 'user.html', {'user_obj_list': user_obj_list, 'page_str': page_str})


@login_required
@check_permission
def add_user(request):
    """创建用户"""
    if request.method == 'GET':
        form_obj = user_form.AddUserForm()
        return render(request, 'add_user.html', {'form_obj': form_obj})
    elif request.method == 'POST':
        form_obj = user_form.AddUserForm(request.POST)
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    user_obj = models.UserProfile.objects.create(**data)
                Logger().log(message='创建用户成功,%s' % user_obj.email, mode=True)
                return redirect('/monitor_web/user.html')
            except Exception as e:
                Logger().log(message='创建用户失败,%s' % str(e), mode=False)
                raise ValidationError(_('添加用户失败'), code='invalid')
        else:
            return render(request, 'add_user.html', {'form_obj': form_obj})


@login_required
@check_permission
def edit_user(request, *args, **kwargs):
    """编辑用户"""
    uid = kwargs['uid']
    if request.method == 'GET':
        form_obj = user_form.EditUserForm(initial={'uid': uid})
        return render(request, 'edit_user.html', {'form_obj': form_obj, 'uid': uid})
    elif request.method == 'POST':
        form_obj = user_form.EditUserForm(request.POST, initial={'uid': uid})
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            try:
                with transaction.atomic():
                    user_obj = models.UserProfile.objects.filter(id=uid).first()
                    models.UserProfile.objects.filter(id=uid).update(**data)
                Logger().log(message='修改用户成功,%s' % user_obj.email, mode=True)
                return redirect('/monitor_web/user.html')
            except Exception as e:
                Logger().log(message='修改用户失败,%s' % str(e), mode=False)
                raise ValidationError(_('修改用户失败'), code='invalid')
        else:
            return render(request, 'edit_user.html', {'form_obj': form_obj, 'uid': uid})


@login_required
@check_permission
def del_user(request):
    """删除用户视图"""
    if request.method == 'POST':
        response = WebResponse()
        user_list = request.POST.getlist('user_list')
        try:
            with transaction.atomic():
                for uid in user_list:
                    uid = int(uid)
                    user_obj = models.UserProfile.objects.filter(id=uid).first()
                    user_obj.delete()
                    Logger().log(message='删除用户成功,%s' % user_obj.email, mode=True)
            response.message = '删除用户成功'
        except Exception as e:
            response.status = False
            response.error = str(e)
            Logger().log(message='删除用户失败,%s' % str(e), mode=False)
        return JsonResponse(response.__dict__)


@login_required
@check_permission
def change_pass_user(request, *args, **kwargs):
    """修改用户密码"""
    uid = kwargs['uid']
    if request.method == 'GET':
        form_obj = user_form.ChangePassUser()
        return render(request, 'change_pass_user.html', {'form_obj': form_obj, 'uid': uid})
    elif request.method == 'POST':
        form_obj = user_form.ChangePassUser(request.POST)
        if form_obj.is_valid():
            password = form_obj.cleaned_data.get('password')
            user_obj = models.UserProfile.objects.get(id=uid)
            user_obj.set_password(password)
            user_obj.save()
            return redirect('/monitor_web/user.html')
        else:
            return render(request, 'change_pass_user.html', {'form_obj': form_obj, 'uid': uid})


@login_required
@check_permission
def change_permission_user(request, *args, **kwargs):
    """修改用户权限"""
    uid = kwargs['uid']
    user_obj = models.UserProfile.objects.get(id=uid)
    all_permission_list = list(Permission.objects.values('id', 'name'))
    user_permission_list = list(user_obj.user_permissions.values('id', 'name'))
    sub_permission_list = []
    for item in all_permission_list:
        if item not in user_permission_list:
            sub_permission_list.append(item)
    if request.method == 'POST':
        try:
            permission_list = request.POST.getlist('permission')
            user_obj.user_permissions.set(permission_list)
            return redirect('/monitor_web/user.html')
        except Exception as e:
            error = str(e)
            return render(request, 'change_permission_user.html', {'uid': uid,
                                                                   'sub_permission_list': sub_permission_list,
                                                                   'user_permission_list': user_permission_list,
                                                                   'error': error})
    elif request.method == 'GET':
        return render(request, 'change_permission_user.html', {'uid': uid,
                                                               'sub_permission_list': sub_permission_list,
                                                               'user_permission_list': user_permission_list})
