#!/usr/bin/env python
# Author: 'JiaChen'

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.http import JsonResponse
from django.conf import settings
from monitor_data import models
from monitor_web.forms import trigger_form
from utils.pagination import Page
from utils.log import Logger
from utils.web_response import WebResponse
from utils.redis_conn import redis_conn


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
