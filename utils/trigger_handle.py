#!/usr/bin/env python
# Author: 'JiaChen'

from utils.redis_conn import redis_conn
import pickle
from monitor_data import models
from django.core.mail import send_mail
from django.conf import settings
import time


class TriggerHandle(object):
    """触发器处理"""
    def __init__(self, settings):
        self.settings = settings
        self.redis = redis_conn(self.settings)
        self.alert_counters = {}    # 纪录每个action的触发报警次数
        '''alert_counters = {
            'CentOS-01': {2:{'counter':0,'last_alert':None}, #k CentOS-01是主机名, {2:{'counter'}} 2是trigger id
                4:{'counter':1,'last_alert':None}},  #k是action id, 
            #2: {2:0},
        }'''
        self.trigger_count = 0  # 触发器计数

    def start_watching(self):
        """开始监听"""
        radio = self.redis.pubsub()
        radio.subscribe(self.settings.TRIGGER_CHAN)
        radio.parse_response()  # 准备好开始
        while True:
            msg = radio.parse_response()
            self.trigger_consume(msg)

    def trigger_consume(self, msg):
        self.trigger_count += 1
        trigger_msg = pickle.loads(msg)
        action = ActionHandle(trigger_msg, self.alert_counters)
        action.trigger_process()


class ActionHandle(object):
    """负责把达到报警条件的trigger进行分析,并根据 action表中的配置来进行报警"""
    def __init__(self, trigger_data, alert_counter_dic):
        self.trigger_data = trigger_data
        self.alert_counter_dic = alert_counter_dic

    def record_log(self, action_obj, action_operation, hostname, trigger_data):
        """将报警日志记录到数据库"""
        models.EventLog.objects.create(
            event_type=0,
            hostname=hostname,
            trigger_id=trigger_data.get('trigger_id'),
            log=trigger_data
        )

    def action_email(self, action_obj, action_operation_obj, hostname, trigger_data):
        """发送报警邮件"""
        notifier_mail_list = [obj.email for obj in action_operation_obj.notifiers.all()]
        subject = '级别:%s -- 主机:%s -- 服务:%s' % (trigger_data.get('trigger_id'),
                                               trigger_data.get('hostname'),
                                               trigger_data.get('service_item'))

        send_mail(
            subject,
            action_operation_obj.msg_format,
            settings.DEFAULT_FROM_EMAIL,
            notifier_mail_list,
        )

    def trigger_process(self):
        """分析触发器并报警"""
        if self.trigger_data.get('trigger_id') == None:
            if self.trigger_data.get('msg'):
                pass    # 既然没有trigger id，直接报警给管理员
            else:
                pass
        else:   # 正经的trigger 报警要触发了
            trigger_id = self.trigger_data.get('trigger_id')
            hostname = self.trigger_data.get('hostname')
            trigger_obj = models.Trigger.objects.filter(id=trigger_id).first()
            actions_set = trigger_obj.action_set.all()  # 找到这个触发器所关联的所有动作
            matched_action_list = set()     # 初始化一个空集合
            for action in actions_set:
                #每个action 都 可以直接 包含多个主机或主机组,
                # 为什么tigger里关联了template,template里又关联了主机，那action还要直接关联主机呢？
                #那是因为一个trigger可以被多个template关联，这个trigger触发了，不一定是哪个tempalte里的主机导致的
                for hg in action.host_groups.select_related():
                    for h in hg.host_set.select_related():
                        if h.id == host_id:# 这个action适用于此主机
                            matched_action_list.add(action)
                            if action.id not in self.alert_counter_dic: #第一次被 触,先初始化一个action counter dic
                                self.alert_counter_dic[action.id] = {}
                            print("action, ",id(action))
                            if h.id not in self.alert_counter_dic[action.id]:  # 这个主机第一次触发这个action的报警
                                self.alert_counter_dic[action.id][h.id] = {'counter': 0, 'last_alert': time.time()}
                                # self.alert_counter_dic.setdefault(action,{h.id:{'counter':0,'last_alert':time.time()}})
                            else:
                                #如果达到报警触发interval次数，就记数+1
                                if time.time() - self.alert_counter_dic[action.id][h.id]['last_alert'] >= action.interval:
                                    self.alert_counter_dic[action.id][h.id]['counter'] += 1
                                    #self.alert_counter_dic[action.id][h.id]['last_alert'] = time.time()

                                else:
                                    print("没达到alert interval时间,不报警",action.interval,
                                          time.time() - self.alert_counter_dic[action.id][h.id]['last_alert'])
                            #self.alert_counter_dic.setdefault(action.id,{})

                for host in action.hosts.select_related():
                    if host.id == host_id:   # 这个action适用于此主机
                        matched_action_list.add(action)
                        if action.id not in self.alert_counter_dic:  # 第一次被 触,先初始化一个action counter dic
                            self.alert_counter_dic[action.id] = {}
                        if h.id not in self.alert_counter_dic[action.id]: #这个主机第一次触发这个action的报警
                            self.alert_counter_dic[action.id][h.id] ={'counter': 0, 'last_alert': time.time()}
                            #self.alert_counter_dic.setdefault(action,{h.id:{'counter':0,'last_alert':time.time()}})
                        else:
                            # 如果达到报警触发interval次数，就记数+1
                            if time.time() - self.alert_counter_dic[action.id][h.id]['last_alert'] >= action.interval:
                                self.alert_counter_dic[action.id][h.id]['counter'] += 1
                                #self.alert_counter_dic[action.id][h.id]['last_alert'] = time.time()
                            else:
                                print("没达到alert interval时间,不报警", action.interval,
                                      time.time() - self.alert_counter_dic[action.id][h.id]['last_alert'])


            print("alert_counter_dic:",self.alert_counter_dic)
            print("matched_action_list:",matched_action_list)
            for action_obj in matched_action_list:#
                if time.time() - self.alert_counter_dic[action_obj.id][host_id]['last_alert'] >= action_obj.interval:
                    #该报警 了
                    print("该报警了.......",time.time() - self.alert_counter_dic[action_obj.id][host_id]['last_alert'],action_obj.interval)
                    for action_operation in action_obj.operations.select_related().order_by('-step'):
                        if action_operation.step > self.alert_counter_dic[action_obj.id][host_id]['counter']:
                            #就
                            print("##################alert action:%s" %
                                  action_operation.action_type,action_operation.notifiers)

                            action_func = getattr(self,'action_%s'% action_operation.action_type)
                            action_func(action_obj,action_operation,host_id,self.trigger_data)

                            #报完警后更新一下报警时间 ，这样就又重新计算alert interval了
                            self.alert_counter_dic[action_obj.id][host_id]['last_alert'] = time.time()
                            self.record_log(action_obj,action_operation,host_id,self.trigger_data)
                        # else:
                        #     print("离下次触发报警的时间还有[%s]s" % )