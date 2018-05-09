#!/usr/bin/env python
# Author: 'JiaChen'

from monitor_data import models
import time
from django.core.mail import send_mail
from django.conf import settings
import json


class ActionHandle(object):
    """负责把达到报警条件的trigger进行分析,并根据action表中的配置来进行报警"""
    def __init__(self, trigger_data, alert_counter_dict_key, redis_obj):
        self.trigger_data = trigger_data
        self.redis_obj = redis_obj
        self.alert_counter_dict_key = alert_counter_dict_key
        self.alert_counter_dict = json.loads(self.redis_obj.get(self.alert_counter_dict_key).decode())

    def record_log(self, hostname, trigger_data):
        """将报警日志记录到数据库"""
        models.EventLog.objects.create(
            event_type=0,
            hosts=models.Host.objects.filter(hostname=hostname).first(),
            triggers_id=trigger_data.get('trigger_id'),
            log=trigger_data
        )

    def action_email(self, action_operation_obj, hostname, trigger_data):
        """发送报警邮件"""
        notifier_mail_list = [user_obj.email for user_obj in action_operation_obj.user_profiles.all()]    # 获取通知邮件列表
        trigger_obj = models.Trigger.objects.filter(id=trigger_data.get('trigger_id')).first()
        application_name = trigger_obj.triggerexpression_set.all()[0].applications.name
        severity_id = trigger_obj.severity
        for severity_list in trigger_obj.severity_choices:
            if severity_id == severity_list[0]:
                severity = severity_list[1]
        subject = '级别:%s -- 主机:%s -- 应用集:%s' % (severity,
                                                trigger_data.get('hostname'),
                                                application_name)
        host_obj = models.Host.objects.filter(hostname=hostname).first()
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(trigger_data['start_time'] + 28800))
        duration = trigger_data['duration']
        if duration is not None:
            if 60 <= duration < 3600:    # 换算成分钟
                duration = '%s分钟' % int(duration/60)
            elif duration < 60:     # 保留整数为秒
                duration = '%s秒' % int(duration)
            else:   # 换算成小时
                duration = '%s小时' % int(duration/60/60)
        else:
            duration = ''
        message = action_operation_obj.msg_format.format(hostname=hostname,
                                                         ip=host_obj.ip,
                                                         name=application_name,
                                                         msg=trigger_data['msg'],
                                                         start_time=start_time,
                                                         duration=duration)
        # 发送邮件
        send_mail(
            subject=subject,    # 主题
            message=message,    # 内容
            from_email=settings.DEFAULT_FROM_EMAIL,     # 发送邮箱
            recipient_list=notifier_mail_list,          # 接收邮箱列表
        )

    def trigger_process(self):
        """分析触发器并报警"""
        '''
        {
            'duration': None, 
            'trigger_id': 3, 
            'start_time': 1525746768.7803395, 
            'hostname': 'CentOS-03_172.16.99.25', 
            'expression_result_list': [
                {'calc_res_val': 1.36, 
                'expression_obj': 3, 
                'specified_item_key': None, 
                'calc_res': True}, 
                {'calc_res_val': 93.21, 
                'expression_obj': 4, 
                'specified_item_key': None, 
                'calc_res': True}
            ], 
            'msg': '内存不足,[SwapUsage_p 1.36>1]、[MemUsage_p 93.21>80]'
        }
        '''
        if self.trigger_data.get('trigger_id') is None:
            if self.trigger_data.get('msg'):
                pass    # 既然没有trigger id直接报警给管理员
        else:   # 正经的trigger报警要触发了
            trigger_id = self.trigger_data.get('trigger_id')    # 获取触发器id
            hostname = self.trigger_data.get('hostname')    # 获取主机名
            trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()  # 获取触发器实例
            action_set = trigger_obj.action_set.all()   # 获取报警策略集合
            for action_obj in action_set:   # 循环每个报警策略
                if str(action_obj.id) not in self.alert_counter_dict:    # 第一次被触发，先初始化一个action_counter_dict
                    self.alert_counter_dict[str(action_obj.id)] = {}
                if hostname not in self.alert_counter_dict[str(action_obj.id)]:  # 这个主机第一次触发这个报警
                    self.alert_counter_dict[str(action_obj.id)][hostname] = {"counter": 1, "last_alert": time.time()}
                    for action_operation_obj in action_obj.action_operations.all().order_by('-step'):
                        if self.alert_counter_dict[str(action_obj.id)][hostname]["counter"] >= action_operation_obj.step:     # 报警计数大于报警升级阈值
                            action_func = getattr(self, 'action_%s' % action_operation_obj.action_type)
                            action_func(action_operation_obj, hostname, self.trigger_data)
                            self.alert_counter_dict[str(action_obj.id)][hostname]["last_alert"] = time.time()    # 报完警后更新一下报警时间，这样就又重新计算报警间隔了
                            self.redis_obj.set(self.alert_counter_dict_key, json.dumps(self.alert_counter_dict))
                            self.record_log(hostname, self.trigger_data)  # 记录日志
                else:
                    # 如果达到报警触发interval次数，就记数+1
                    if time.time() - self.alert_counter_dict[str(action_obj.id)][hostname]["last_alert"] >= action_obj.interval:
                        self.alert_counter_dict[str(action_obj.id)][hostname]["counter"] += 1
                        for action_operation_obj in action_obj.action_operations.all().order_by('-step'):
                            if self.alert_counter_dict[str(action_obj.id)][hostname]["counter"] >= action_operation_obj.step:  # 报警计数大于报警升级阈值
                                action_func = getattr(self, 'action_%s' % action_operation_obj.action_type)
                                action_func(action_operation_obj, hostname, self.trigger_data)
                                self.alert_counter_dict[str(action_obj.id)][hostname]["last_alert"] = time.time()  # 报完警后更新一下报警时间，这样就又重新计算报警间隔了
                                self.redis_obj.set(self.alert_counter_dict_key, json.dumps(self.alert_counter_dict))
                                self.record_log(hostname, self.trigger_data)  # 记录日志
