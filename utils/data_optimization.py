#!/usr/bin/env python
# Author: 'JiaChen'

from django.conf import settings
import json
import time
import copy


class DataStore(object):
    """处理客户端报告的服务数据，做一些数据优化并将其保存到redis数据库中"""

    def __init__(self, hostname, application_name, data, redis_obj, response):
        self.hostname = hostname
        self.application_name = application_name
        self.data = data
        self.redis_obj = redis_obj
        self.response = response
        self.process_and_save()

    def process_and_save(self):
        """处理并保存数据到redis中"""
        # self.data {'iowait': 0.33, 'idle': 98.33, 'system': 1.0, 'status': 0, 'user': 0.33}
        if self.data['status'] == 0:  # 汇报数据是有效的
            del self.data['status']  # 将状态信息从数据中删除
            for key, value in settings.DATA_OPTIMIZATION.items():
                data_optimize_interval, max_data_point = value  # 获取数据优化间隔和最大存储点
                data_key_in_redis = 'StatusData_%s_%s_%s' % (
                    self.hostname, self.application_name, key)  # 获取对应主机应用集下的key名称
                last_point_from_redis = self.redis_obj.lrange(name=data_key_in_redis, start=-1, end=-1)  # 取key最后一个点的值
                if not last_point_from_redis:  # 这个key在redis中不存在
                    # 所以初始化一个新键，数据集中的第一个数据点只会被用来识别上次数据被保存的时候
                    self.redis_obj.rpush(data_key_in_redis, json.dumps([None, time.time()]))
                if data_optimize_interval == 0:  # 这个数据集用于未优化的数据，只有最新的数据不需要优化
                    self.redis_obj.rpush(data_key_in_redis, json.dumps([self.data, time.time()]))
                else:  # 需要优化的数据
                    last_point_data, last_point_save_time = json.loads(
                        self.redis_obj.lrange(name=data_key_in_redis, start=-1, end=-1)[0].decode()
                    )   # 最后一个点的数据和最后一个点的存储时间
                    if time.time() - last_point_save_time >= data_optimize_interval:  # 到达数据点更新间隔
                        lastest_data_key_in_redis = 'StatusData_%s_%s_latest' % (
                            self.hostname, self.application_name
                        )
                        # 取最近n分钟的数据,放到了data_set里
                        data_set = self.get_data_slice(lastest_data_key_in_redis, data_optimize_interval)
                        if len(data_set) > 0:
                            # 接下来拿这个data_set交给下面的方法，算出优化结果
                            optimized_data = self.get_optimized_data(data_key_in_redis, data_set)
                            if optimized_data:  # 如果优化数据存在
                                self.save_optimized_data(data_key_in_redis, optimized_data)     # 保存优化数据
                if self.redis_obj.llen(data_key_in_redis) >= max_data_point:    # 如果数据列表点数大于最大数据点数
                    self.redis_obj.lpop(data_key_in_redis)      # 删除最旧的一个点的数据
            return self.response
        else:  # 汇报数据是无效的
            self.response['code'] = 422
            self.response['message'] = '服务器判定为无效数据,%s' % self.data
            return self.response

    def get_data_slice(self, lastest_data_key_in_redis, data_optimize_interval):
        """获取redis数据库中一段时间的切片数据"""
        all_real_data = self.redis_obj.lrange(name=lastest_data_key_in_redis, start=1, end=-1)
        data_set = []
        for item in all_real_data:
            data = json.loads(item.decode())
            if len(data) == 2:
                application_data, last_save_time = data
                if time.time() - last_save_time <= data_optimize_interval:  # 在优化时间内
                    data_set.append(data)
        return data_set

    def get_optimized_data(self, data_key_in_redis, data_set):
        """获取优化数据"""
        '''
         data_set = [
            [{\"user\": 0.33, \"system\": 1.34, \"idle\": 98.33, \"iowait\": 0.0}, 1523868963.8312852],
            [{\"user\": 1.0, \"system\": 3.68, \"idle\": 95.32, \"iowait\": 0.0}, 1523868993.89751],
            [{\"user\": 0.0, \"system\": 1.68, \"idle\": 98.32, \"iowait\": 0.0}, 1523869024.0294662],
        ]
         data_set = [
            [{\"data\": {\"lo\": {\"t_out\": 0.0, \"t_in\": 0.0}, \"eth0\": {\"t_out\": 2.03, \"t_in\": 65.82}}}, 1523869898.9049253],
            [{\"data\": {\"lo\": {\"t_out\": 0.0, \"t_in\": 0.0}, \"eth0\": {\"t_out\": 1.87, \"t_in\": 65.46}}}, 1523869959.0638402],
            [{\"data\": {\"lo\": {\"t_out\": 0.0, \"t_in\": 0.0}, \"eth0\": {\"t_out\": 2.0, \"t_in\": 65.86}}}, 1523870019.2523856],
        ]
       '''
        application_data_keys = data_set[0][0].keys()   # ['user', 'idle'] or ['data']
        first_application_data_point = data_set[0][0]   # 用这个来构建一个新的空字典
        optimized_data = {}     # 设置一个空字典，用来保存最终优化数据
        if 'data' not in application_data_keys:     # 意味着这个字典没有子字典，用于像cpu、内存这样的服务
            for key in application_data_keys:
                optimized_data[key] = []    # {'user': [], 'idle': []}
            tmp_data_dict = copy.deepcopy(optimized_data)   # 为了临时存最近n分钟的数据,把它们按照每个指标都搞成一个一个列表 ,来存最近N分钟的数据
            for item_application_data, last_save_time in data_set:  # 循环最近n分钟的数据
                for items_name, value in item_application_data.items():     # 循环每个数据点的指标，items_name监控项名如idle,value为监控的值
                    try:
                        tmp_data_dict[items_name].append(value)
                    except Exception as e:
                        pass
            for application_k, v_list in tmp_data_dict.items():     # application_k idle,v_list [98.33, 99.22, 93.55]
                avg_res = self.get_average(v_list)  # 取平均值
                max_res = self.get_max(v_list)  # 取最大值
                min_res = self.get_min(v_list)  # 取最小值
                mid_res = self.get_mid(v_list)  # 取中间值
                optimized_data[application_k] = [avg_res, max_res, min_res, mid_res]    # 将计算结果保存到最终的优化数据字典中
        else:   # 意味着这个字典有子字典，用于像硬盘、网卡这样的服务
            for application_item_key, v_dict in first_application_data_point['data'].items():   # 应用集下监控项key和值的字典
                optimized_data['application_item_key'] = {}
                for k2, v2 in v_dict.items():
                    optimized_data['application_item_key'][k2] = []     # {'eth0': {'t_in': [], 't_out': []}}
            tmp_data_dict = copy.deepcopy(optimized_data)
            if tmp_data_dict:   # 由于客户端汇报数据有误，有可能为空
                for item_application_data, last_save_time in data_set:  # 循环最近n分钟数据
                    for name, value_dict in item_application_data['data'].items():    # name如eth0,value为监控的值的字典
                        for items_name, value in value_dict.items():    # 循环每个数据点的指标，items_name监控项名如in_t,value为监控的值
                            tmp_data_dict[name][items_name].append(value)
                for name, v_dict in tmp_data_dict.items():
                    for items_name, v_list in v_dict.items():
                        avg_res = self.get_average(v_list)
                        max_res = self.get_max(v_list)
                        min_res = self.get_min(v_list)
                        mid_res = self.get_mid(v_list)
                        optimized_data[name][items_name] = [avg_res, max_res, min_res, mid_res]
            else:   # 客户端汇报的数据一定是错误的
                pass
        print('优化后的数据----->', optimized_data)
        return optimized_data

    def get_average(self, v_list):
        """获取平均值"""
        if len(v_list) > 0:
            return sum(v_list)/len(v_list)
        else:
            return 0

    def get_max(self, v_list):
        """获取最大值"""
        if len(v_list) > 0:
            return max(v_list)
        else:
            return 0

    def get_min(self, v_list):
        """获取最小值"""
        if len(v_list) > 0:
            return min(v_list)
        else:
            return 0

    def get_mid(self, v_list):
        """获取中间值"""
        v_list = v_list.sort()
        if len(v_list) > 0:
            return v_list[int(len(v_list)/2)]
        else:
            return 0

    def save_optimized_data(self, data_key_in_redis, optimized_data):
        """保存优化后的数据"""
        self.redis_obj.rpush(data_key_in_redis, json.dumps([optimized_data, time.time()]))
