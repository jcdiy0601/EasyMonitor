#!/usr/bin/env python
# Author: 'JiaChen'

from django.conf import settings
import time
from utils.redis_conn import redis_conn
import json


class DataHandler(object):
    """"""

    def __init__(self, connect_redis=True):
        self.poll_interval = 3  # 每3秒进行一次全局轮训
        self.config_update_interval = 120  # 每120s重新从数据库加载一次配置数据
        self.config_last_loading_time = time.time()  # 配置最后加载时间
        self.global_monitor_dic = {}
        self.exit_flag = False
        if connect_redis:
            self.redis = redis_conn(settings)

    def load_application_data_and_calulating(self, host_obj, trigger_obj, redis_obj):
        """
        从redis db中获取数据，并根据每个应用集的触发器配置进行计算
        :param host_obj:
        :param trigger_obj: 应用集的触发器
        :param redis_obj: 从外面调用此函数时需传入redis_obj,以减少重复连接
        :return:
        """
        self.redis = redis_obj
        calc_sub_res_list = []  # 先把每个expression的结果算出来放在这个列表里,最后再统一计算这个列表
        positive_expressions = []
        expression_res_string = ''
        for expression_obj in trigger_obj.triggerexpression_set.all().order_by('id'):  # 循环触发器下所有触发器表达式
            expression_process_obj = ExpressionProcess(self, host_obj, expression_obj)
            single_expression_res = expression_process_obj.process()  # 得到单条expression表达式的结果


class ExpressionProcess(object):
    """通过不同的方法加载和计算数据"""
    def __init__(self, main_ins, host_obj, expression_obj, specified_item=None):
        """
        :param main_ins: DataHandler 实例
        :param host_obj:
        :param expression_obj:
        """
        self.host_obj = host_obj
        self.expression_obj = expression_obj
        self.main_ins = main_ins
        self.lastest_data_key_in_redis = 'StatusData_%s_%s_latest' % (host_obj.hostname, expression_obj.applications.name)
        self.time_range = json.loads(self.expression_obj.data_calc_func_args)['time']   # 获取要从redis中取多长时间的数据,单位为minute

    def load_data_from_redis(self):
        """根据表达式的配置从redis加载数据"""
        time_in_sec = int(self.time_range) * 60     # 换算时间范围分钟->秒
        approximate_data_points = int((time_in_sec + 60) / self.expression_obj.applications.interval)    # 获取一个大概要取的点的数量,+60是默认多取一分钟数据,宁多勿少,多出来的后面会去掉
        data_range_raw = self.main_ins.redis.lrange(self.lastest_data_key_in_redis, -approximate_data_points, -1)   # 从redis中获取大概范围点的数据
        approximate_data_range = [json.loads(i.decode()) for i in data_range_raw]   # 大概的数据
        data_range = []     # 精确的数据列表
        for point in approximate_data_range:
            pass

    def process(self):
        """算出单条expression表达式的结果"""
        data_list = self.load_data_from_redis() # 已经按照用户的配置把数据 从redis里取出来了, 比如 最近5分钟,或10分钟的数据