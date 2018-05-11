#!/usr/bin/env python
# Author: 'JiaChen'

import os
import sys
import django
import time
import atexit
import subprocess
from signal import SIGTERM
from django.conf import settings
django.setup()
from utils.data_processing import DataHandle
from utils.trigger_handle import TriggerHandle


class ManagementUtility(object):
    """封装了django-admin和manage的逻辑,py工具管理实用程序有许多命令，它们可以被操纵,通过编辑self.command字典"""
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]     # 参数
        # self.script_name = os.path.basename(self.argv[0])   # 脚本名称
        # self.settings_exception = None
        self.registered_action_dict = {
            'start': self.start,    # 开启主机检测
            'stop': self.stop,  # 关闭主机检测
            'status': self.status,  # 查看主机检测服务状态
            'trigger_watch_start': self.trigger_watch_start,    # 开启触发器检测
            'trigger_watch_stop': self.trigger_watch_stop,  # 关闭
            'trigger_watch_status': self.trigger_watch_status
        }
        self.trigger_watch_pid = settings.TRIGGER_WATCH_PID_FILE    # trigger_watch pid文件路径
        self.host_alive_pid = settings.HOST_ALIVE_PID_FILE  # host_alive pid文件路径

    def check_and_execute(self):
        """基本参数验证检查"""
        if len(self.argv) < 2:  # 判断输入参数数量
            self.main_help_text()
        if self.argv[1] not in self.registered_action_dict:     # 判断参数是否在设置好的已注册动作字典中
            self.main_help_text()
        else:   # 检测通过
            self.registered_action_dict[sys.argv[1]]()      # 执行注册方法

    def trigger_watch_start(self):
        """开始监听触发器"""
        print('启动监听触发器服务...')
        time.sleep(1)
        # pid = os.fork()
        # # 父进程(会话组头领进程)退出，这意味着一个非会话组头领进程永远不能重新获得控制终端
        # if pid > 0:
        #     sys.exit(0)  # 父进程退出
        # # 从母体环境脱离
        # os.chdir('/')  # chdir确认进程不保持任何目录于使用状态，否则不能umount一个文件系统，也可以改变到对于守护程序运行重要的文件所在目录
        # os.umask(0)  # 调用umask(0)以便拥有对于写的任何东西的完全控制，因为有时不知道继承了什么样的umask
        # os.setsid()  # setsid调用成功后，进程成为新的会话组长和新的进程组长，并与原来的登录会话和进程组脱离
        # # 执行第二次fork
        # pid = os.fork()
        # if pid > 0:
        #     sys.exit(0)  # 第二个父进程退出
        # # 进程已经是守护进程了，重定向标准文件描述符
        # sys.stdout.flush()
        # sys.stderr.flush()
        # # dup2函数原子化地关闭和复制文件描述符，重定向到/dev/nul，即丢弃所有输入输出
        # with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        #     os.dup2(read_null.fileno(), sys.stdin.fileno())
        #     os.dup2(write_null.fileno(), sys.stdout.fileno())
        #     os.dup2(write_null.fileno(), sys.stderr.fileno())
        # # 写入pid文件
        # with open(self.trigger_watch_pid, 'w') as f:
        #     f.write(str(os.getpid()))
        trigger_handle_obj = TriggerHandle()
        trigger_handle_obj.start_watching()

    def trigger_watch_stop(self):
        """关闭监听触发器"""
        try:
            with open(self.trigger_watch_pid, 'r') as f:
                pid = int(f.read().strip())
                os.kill(pid, SIGTERM)
        except Exception as e:
            print('监听触发器服务未启动...')
            sys.exit(1)
        atexit.register(os.remove, self.trigger_watch_pid)
        print('关闭监听触发器服务...')
        time.sleep(1)

    def trigger_watch_status(self):
        """查看监听触发器状态"""
        if os.path.isfile(self.trigger_watch_pid):
            with open(self.trigger_watch_pid, 'r') as f:
                pid = f.read().strip()
                shell_command = 'ps -ef | grep -v grep | grep %s' % pid
                result = subprocess.getoutput(shell_command)
                if result:
                    print('监听触发器服务运行中...')
        else:
            print('监听触发器服务未启动...')

    def start(self):
        """启动主机存活检测服务"""
        print('启动主机存活检测服务...')
        time.sleep(1)
        # pid = os.fork()
        # # 父进程(会话组头领进程)退出，这意味着一个非会话组头领进程永远不能重新获得控制终端
        # if pid > 0:
        #     sys.exit(0)  # 父进程退出
        # # 从母体环境脱离
        # os.chdir('/')  # chdir确认进程不保持任何目录于使用状态，否则不能umount一个文件系统，也可以改变到对于守护程序运行重要的文件所在目录
        # os.umask(0)  # 调用umask(0)以便拥有对于写的任何东西的完全控制，因为有时不知道继承了什么样的umask
        # os.setsid()  # setsid调用成功后，进程成为新的会话组长和新的进程组长，并与原来的登录会话和进程组脱离
        # # 执行第二次fork
        # pid = os.fork()
        # if pid > 0:
        #     sys.exit(0)  # 第二个父进程退出
        # # 进程已经是守护进程了，重定向标准文件描述符
        # sys.stdout.flush()
        # sys.stderr.flush()
        # # dup2函数原子化地关闭和复制文件描述符，重定向到/dev/nul，即丢弃所有输入输出
        # with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        #     os.dup2(read_null.fileno(), sys.stdin.fileno())
        #     os.dup2(write_null.fileno(), sys.stdout.fileno())
        #     os.dup2(write_null.fileno(), sys.stderr.fileno())
        # # 写入pid文件
        # with open(self.host_alive_pid, 'w') as f:
        #     f.write(str(os.getpid()))
        data_handle_obj = DataHandle()
        data_handle_obj.looping()

    def stop(self):
        """关闭主机存活检测服务"""
        try:
            with open(self.host_alive_pid, 'r') as f:
                pid = int(f.read().strip())
                os.kill(pid, SIGTERM)
        except Exception as e:
            print('主机存活检测服务未启动...')
            sys.exit(1)
        atexit.register(os.remove, self.host_alive_pid)
        print('关闭主机存活检测服务...')
        time.sleep(1)

    def status(self):
        """查看主机存活检测服务状态"""
        if os.path.isfile(self.host_alive_pid):
            with open(self.host_alive_pid, 'r') as f:
                pid = f.read().strip()
                shell_command = 'ps -ef | grep -v grep | grep %s' % pid
                result = subprocess.getoutput(shell_command)
                if result:
                    print('主机存活检测服务运行中...')
        else:
            print('主机存活检测服务未启动...')

    def main_help_text(self, commands_only=False):
        """返回脚本帮助信息"""
        if not commands_only:
            print('支持命令:')
            for k, v in self.registered_action_dict.items():
                print('     %s%s' % (k.ljust(20), v.__doc__))
            exit()


def execute_from_command_line(argv=None):
    """管理应用程序的一个简单方法"""
    utility = ManagementUtility(argv)
    utility.check_and_execute()
