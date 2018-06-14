#!/usr/bin/env python
# _*_ coding:utf-8 _*_
# Author: JiaChen

from django.shortcuts import render, redirect
from django.core.urlresolvers import resolve

perm_dic = {
    # 用户
    # 可访问用户页面
    'monitor_data.can_show_user': {
        'url_type': 0,       # 0代表相对路径，1代表绝对路径
        'url': 'user',       # url
        'method': 'GET',     # 请求方式
        'args': [],          # 请求参数
    },
    # 可访问创建用户页面
    'monitor_data.can_show_add_user': {
        'url_type': 0,
        'url': 'add_user',
        'method': 'GET',
        'args': []
    },
    # 可创建用户
    'monitor_data.can_add_user': {
        'url_type': 0,
        'url': 'add_user',
        'method': 'POST',
        'args': []
    },
    # 可删除用户
    'monitor_data.can_del_user': {
        'url_type': 0,
        'url': 'del_user',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑用户页面
    'monitor_data.can_show_edit_user': {
        'url_type': 0,
        'url': 'edit_user',
        'method': 'GET',
        'args': []
    },
    # 可编辑用户
    'monitor_data.can_edit_user': {
        'url_type': 0,
        'url': 'edit_user',
        'method': 'POST',
        'args': []
    },
    # 可访问重置密码页面
    'monitor_data.can_show_change_pass_user': {
        'url_type': 0,
        'url': 'change_pass_user',
        'method': 'GET',
        'args': []
    },
    # 可重置密码
    'monitor_data.can_change_pass_user': {
        'url_type': 0,
        'url': 'change_pass_user',
        'method': 'POST',
        'args': []
    },
    # 可访问修改权限页面
    'monitor_data.can_show_change_permission_user': {
        'url_type': 0,
        'url': 'change_permission_user',
        'method': 'GET',
        'args': []
    },
    # 可修改权限
    'monitor_data.can_change_permission_user': {
        'url_type': 0,
        'url': 'change_permission_user',
        'method': 'POST',
        'args': []
    },
    # 主机
    # 可访问主机页面
    'monitor_data.can_show_host': {
        'url_type': 0,
        'url': 'host',
        'method': 'GET',
        'args': []
    },
    # 可访问创建主机页面
    'monitor_data.can_show_add_host': {
        'url_type': 0,
        'url': 'add_host',
        'method': 'GET',
        'args': []
    },
    # 可创建主机
    'monitor_data.can_add_host': {
        'url_type': 0,
        'url': 'add_host',
        'method': 'POST',
        'args': []
    },
    # 可删除主机
    'monitor_data.can_del_host': {
        'url_type': 0,
        'url': 'del_host',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑主机页面
    'monitor_data.can_show_edit_host': {
        'url_type': 0,
        'url': 'edit_host',
        'method': 'GET',
        'args': []
    },
    # 可编辑主机
    'monitor_data.can_edit_host': {
        'url_type': 0,
        'url': 'edit_host',
        'method': 'POST',
        'args': []
    },
    # 主机组
    # 可访问主机组页面
    'monitor_data.can_show_host_group': {
        'url_type': 0,
        'url': 'host_group',
        'method': 'GET',
        'args': []
    },
    # 可访问创建主机组页面
    'monitor_data.can_show_add_host_group': {
        'url_type': 0,
        'url': 'add_host_group',
        'method': 'GET',
        'args': []
    },
    # 可创建主机组
    'monitor_data.can_add_host_group': {
        'url_type': 0,
        'url': 'add_host_group',
        'method': 'POST',
        'args': []
    },
    # 可删除主机组
    'monitor_data.can_del_host_group': {
        'url_type': 0,
        'url': 'del_host_group',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑主机组页面
    'monitor_data.can_show_edit_host_group': {
        'url_type': 0,
        'url': 'del_host_group',
        'method': 'GET',
        'args': []
    },
    # 可编辑主机组
    'monitor_data.can_edit_host_group': {
        'url_type': 0,
        'url': 'del_host_group',
        'method': 'POST',
        'args': []
    },
    # 应用集
    # 可访问应用集页面
    'monitor_data.can_show_application': {
        'url_type': 0,
        'url': 'application',
        'method': 'GET',
        'args': []
    },
    # 可访问创建应用集页面
    'monitor_data.can_show_add_application': {
        'url_type': 0,
        'url': 'add_application',
        'method': 'GET',
        'args': []
    },
    # 可创建应用集
    'monitor_data.can_add_application': {
        'url_type': 0,
        'url': 'add_application',
        'method': 'POST',
        'args': []
    },
    # 可删除应用集
    'monitor_data.can_del_application': {
        'url_type': 0,
        'url': 'del_application',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑应用集页面
    'monitor_data.can_show_edit_application': {
        'url_type': 0,
        'url': 'edit_application',
        'method': 'GET',
        'args': []
    },
    # 可编辑应用集
    'monitor_data.can_edit_application': {
        'url_type': 0,
        'url': 'edit_application',
        'method': 'POST',
        'args': []
    },
    # 监控项
    # 可访问监控项页面
    'monitor_data.can_show_item': {
        'url_type': 0,
        'url': 'item',
        'method': 'GET',
        'args': []
    },
    # 可访问创建监控项页面
    'monitor_data.can_show_add_item': {
        'url_type': 0,
        'url': 'add_item',
        'method': 'GET',
        'args': []
    },
    # 可创建监控项
    'monitor_data.can_add_item': {
        'url_type': 0,
        'url': 'add_item',
        'method': 'POST',
        'args': []
    },
    # 可删除监控项
    'monitor_data.can_del_item': {
        'url_type': 0,
        'url': 'del_item',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑监控项页面
    'monitor_data.can_show_edit_item': {
        'url_type': 0,
        'url': 'edit_item',
        'method': 'GET',
        'args': []
    },
    # 可编辑监控项
    'monitor_data.can_edit_item': {
        'url_type': 0,
        'url': 'edit_item',
        'method': 'POST',
        'args': []
    },
    # 模板
    # 可访问模板页面
    'monitor_data.can_show_template': {
        'url_type': 0,
        'url': 'template',
        'method': 'GET',
        'args': []
    },
    # 可访问创建模板页面
    'monitor_data.can_show_add_template': {
        'url_type': 0,
        'url': 'add_template',
        'method': 'GET',
        'args': []
    },
    # 可创建模板
    'monitor_data.can_add_template': {
        'url_type': 0,
        'url': 'add_template',
        'method': 'POST',
        'args': []
    },
    # 可删除模板
    'monitor_data.can_del_template': {
        'url_type': 0,
        'url': 'del_template',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑模板页面
    'monitor_data.can_show_edit_template': {
        'url_type': 0,
        'url': 'edit_template',
        'method': 'GET',
        'args': []
    },
    # 可编辑模板
    'monitor_data.can_edit_template': {
        'url_type': 0,
        'url': 'edit_template',
        'method': 'POST',
        'args': []
    },
    # 触发器
    # 可访问触发器页面
    'monitor_data.can_show_trigger': {
        'url_type': 0,
        'url': 'trigger',
        'method': 'GET',
        'args': []
    },
    # 可访问创建触发器页面
    'monitor_data.can_show_add_trigger': {
        'url_type': 0,
        'url': 'add_trigger',
        'method': 'GET',
        'args': []
    },
    # 可创建触发器
    'monitor_data.can_add_trigger': {
        'url_type': 0,
        'url': 'add_trigger',
        'method': 'POST',
        'args': []
    },
    # 可删除触发器
    'monitor_data.can_del_trigger': {
        'url_type': 0,
        'url': 'del_trigger',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑触发器页面
    'monitor_data.can_show_edit_trigger': {
        'url_type': 0,
        'url': 'edit_trigger',
        'method': 'GET',
        'args': []
    },
    # 可编辑触发器
    'monitor_data.can_edit_trigger': {
        'url_type': 0,
        'url': 'edit_trigger',
        'method': 'POST',
        'args': []
    },
    # 报警策略
    # 可访问报警策略页面
    'monitor_data.can_show_action': {
        'url_type': 0,
        'url': 'action',
        'method': 'GET',
        'args': []
    },
    # 可访问创建报警策略页面
    'monitor_data.can_show_add_action': {
        'url_type': 0,
        'url': 'add_action',
        'method': 'GET',
        'args': []
    },
    # 可创建报警策略
    'monitor_data.can_add_action': {
        'url_type': 0,
        'url': 'add_action',
        'method': 'POST',
        'args': []
    },
    # 可删除报警策略
    'monitor_data.can_del_action': {
        'url_type': 0,
        'url': 'del_action',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑报警策略页面
    'monitor_data.can_show_edit_action': {
        'url_type': 0,
        'url': 'edit_action',
        'method': 'GET',
        'args': []
    },
    # 可编辑报警策略
    'monitor_data.can_edit_action': {
        'url_type': 0,
        'url': 'edit_action',
        'method': 'POST',
        'args': []
    },
    # 报警动作
    # 可访问报警动作页面
    'monitor_data.can_show_action_operation': {
        'url_type': 0,
        'url': 'action_operation',
        'method': 'GET',
        'args': []
    },
    # 可访问创建报警动作页面
    'monitor_data.can_show_add_action_operation': {
        'url_type': 0,
        'url': 'add_action_operation',
        'method': 'GET',
        'args': []
    },
    # 可创建报警动作
    'monitor_data.can_add_action_operation': {
        'url_type': 0,
        'url': 'add_action_operation',
        'method': 'POST',
        'args': []
    },
    # 可删除报警动作
    'monitor_data.can_del_action_operation': {
        'url_type': 0,
        'url': 'del_action_operation',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑报警动作页面
    'monitor_data.can_show_edit_action_operation': {
        'url_type': 0,
        'url': 'edit_action_operation',
        'method': 'GET',
        'args': []
    },
    # 可编辑报警动作
    'monitor_data.can_edit_action_operation': {
        'url_type': 0,
        'url': 'edit_action_operation',
        'method': 'POST',
        'args': []
    },
    # 图表
    # 可访问图表页面
    'monitor_data.can_show_chart': {
        'url_type': 0,
        'url': 'chart',
        'method': 'GET',
        'args': []
    },
    # 可访问创建图表页面
    'monitor_data.can_show_add_chart': {
        'url_type': 0,
        'url': 'add_chart',
        'method': 'GET',
        'args': []
    },
    # 可创建图表
    'monitor_data.can_add_chart': {
        'url_type': 0,
        'url': 'add_chart',
        'method': 'POST',
        'args': []
    },
    # 可删除图表
    'monitor_data.can_del_chart': {
        'url_type': 0,
        'url': 'del_chart',
        'method': 'POST',
        'args': []
    },
    # 可访问编辑图表页面
    'monitor_data.can_show_edit_chart': {
        'url_type': 0,
        'url': 'edit_chart',
        'method': 'GET',
        'args': []
    },
    # 可编辑图表
    'monitor_data.can_edit_chart': {
        'url_type': 0,
        'url': 'edit_chart',
        'method': 'POST',
        'args': []
    }
}


def perm_check(*args, **kwargs):
    """
    检查权限
    :param args:
    :param kwargs:
    :return:
    """
    request = args[0]
    if request.user.is_authenticated():     # 登录状态
        for permission_name, permission_info in perm_dic.items():
            url_matched = False
            if permission_info['url_type'] == 1:    # url为绝对路径
                if permission_info['url'] == request.path:  # 绝对路径匹配上了
                    url_matched = True
            else:   # url是相对路径，要把绝对的url请求转成相对的url name
                resolve_url_obj = resolve(request.path)
                current_url_name = resolve_url_obj.url_name
                if permission_info['url'] == current_url_name:  # 相对的url别名匹配上了
                    url_matched = True
            if url_matched:
                if permission_info['method'] == request.method:     # 请求方法也匹配上了
                    arg_matched = True
                    for request_arg in permission_info['args']:
                        request_method_func = getattr(request, permission_info['method'])
                        if not request_method_func.get(request_arg):
                            arg_matched = False
                    if arg_matched:     # 走到这里，仅仅代表这个请求和这条权限的定义规则匹配上了
                        if request.user.has_perm(permission_name):
                            return True     # 有权限
    else:
        redirect('/login.html')


def check_permission(func):
    """
    装饰器
    :param func:
    :return:
    """
    def inner(*args, **kwargs):
        request = args[0]
        if perm_check(*args, **kwargs) is True:
            return func(*args, **kwargs)
        else:
            return render(request, '403.html')
    return inner
