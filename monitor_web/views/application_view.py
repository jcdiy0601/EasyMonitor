#!/usr/bin/env python
# Author: 'JiaChen'

import requests
import json
import hashlib
import time
import re
from django.conf import settings
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
from utils.redis_conn import redis_conn


@login_required
def application(request):
    """应用集视图"""
    return render(request, 'application.html')


@login_required
def add_application(request):
    """创建应用集视图"""
    pass


@login_required
def edit_application(request):
    """编辑应用集视图"""
    pass


@login_required
def del_application(request):
    """删除应用集视图"""
    pass

