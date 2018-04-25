#!/usr/bin/env python
# Author: 'JiaChen'

import os
import sys
import django
django.setup()
from utils import data_processing
from utils.trigger_handle import TriggerHandler
from django.conf import settings


class ManagementUtility(object):
    """封装了django-admin和manage的逻辑,py工具管理实用程序有许多命令，它们可以被操纵,通过编辑self.command字典"""
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
        self.settings_exception = None
        self.registered_actions = {
            'start': self.start,
            'stop': self.stop,
            'trigger_watch': self.trigger_watch
        }
        self.argv_check()

    def argv_check(self):
        """基本参数验证检查"""
        if len(self.argv) < 2:
            self.main_help_text()
        if self.argv[1] not in self.registered_actions:
            self.main_help_text()
        else:
            self.registered_actions[sys.argv[1]]()

    def start(self):
        """启动监控服务"""
        reactor = data_processing.DataHandler(settings)
        reactor.looping()

    def stop(self):
        """关闭监控服务"""
        pass

    def trigger_watch(self):
        """开始监听触发器"""
        trigger_watch = TriggerHandler(settings)

    def main_help_text(self, commands_only=False):
        """返回脚本帮助信息"""
        if not commands_only:
            print('支持命令:')
            for k, v in self.registered_actions.items():
                print('     %s%s' % (k.ljust(20), v.__doc__))
            exit()

    def execute(self):
        """根据用户输入运行"""
        pass


def execute_from_command_line(argv=None):
    """管理应用程序的一个简单方法"""
    utility = ManagementUtility(argv)
    utility.execute()
