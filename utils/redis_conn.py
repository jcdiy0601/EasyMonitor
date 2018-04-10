#!/usr/bin/env python
# Author: 'JiaChen'

import redis


def redis_conn(django_settings):
    """redis连接函数，对redis服务器进行连接"""
    pool = redis.ConnectionPool(host=django_settings.REDIS_CONN['HOST'],
                                port=django_settings.REDIS_CONN['PORT'],
                                db=django_settings.REDIS_CONN['DB'])
    r = redis.Redis(connection_pool=pool)
    return r
