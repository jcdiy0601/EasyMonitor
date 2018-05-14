#!/usr/bin/env python
# Author: 'JiaChen'

import time
from django.core.mail import send_mail
from django.conf import settings
from monitor_data import models
from utils.log import Logger


def email(action_operation_obj, hostname, trigger_data, action_obj, status=True):
    """邮件通知"""
    trigger_id = trigger_data.get('trigger_id')
    trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()  # 获取触发器实例
    severity = trigger_obj.severity
    for severity_list in trigger_obj.severity_choices:
        if severity == severity_list[0]:
            severity = severity_list[1]
    application_name = trigger_obj.triggerexpression_set.all()[0].applications.name
    subject = '级别:%s -- 主机:%s -- 应用集:%s' % (severity, hostname, application_name)  # 邮件主题
    host_obj = models.Host.objects.filter(hostname=hostname).first()
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(trigger_data['start_time'] + 28800))
    duration = trigger_data.get('duration')
    if duration is not None:
        if 60 <= duration < 3600:  # 换算成分钟
            duration = '%s分钟' % int(duration / 60)
        elif duration < 60:  # 保留整数为秒
            duration = '%s秒' % int(duration)
        else:  # 换算成小时
            duration = '%s小时' % int(duration / 60 / 60)
    else:
        duration = ''
    if status is True:  # 恢复邮件
        msg = trigger_obj.name
        recover_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + 28800))
        message = action_obj.recover_msg_format.format(hostname=hostname,
                                                       ip=host_obj.ip,
                                                       name=application_name,
                                                       msg=msg,
                                                       start_time=start_time,
                                                       duration=duration,
                                                       recover_time=recover_time)
        # 使用django send_mail发送邮件
        notifier_mail_list = [user_obj.email for user_obj in action_operation_obj.user_profiles.all()]  # 获取通知邮件列表
        send_mail(
            subject=subject,  # 主题
            message=message,  # 内容
            from_email=settings.DEFAULT_FROM_EMAIL,  # 发送邮箱
            recipient_list=notifier_mail_list,  # 接收邮箱列表
        )
        Logger().log(message='发送恢复邮件通知,%s,%s,%s,%s' % (subject, message,
                                                       settings.DEFAULT_FROM_EMAIL,
                                                       notifier_mail_list),
                     mode=True)
    else:   # 报警邮件
        msg = trigger_data.get('msg')
        message = action_obj.alert_msg_format.format(hostname=hostname,
                                                     ip=host_obj.ip,
                                                     name=application_name,
                                                     msg=msg,
                                                     start_time=start_time,
                                                     duration=duration)
        # 使用django send_mail发送邮件
        notifier_mail_list = [user_obj.email for user_obj in action_operation_obj.user_profiles.all()]  # 获取通知邮件列表
        send_mail(
            subject=subject,  # 主题
            message=message,  # 内容
            from_email=settings.DEFAULT_FROM_EMAIL,  # 发送邮箱
            recipient_list=notifier_mail_list,  # 接收邮箱列表
        )
        Logger().log(message='发送报警邮件通知,%s,%s,%s,%s' % (subject, message,
                                                       settings.DEFAULT_FROM_EMAIL,
                                                       notifier_mail_list),
                     mode=True)
