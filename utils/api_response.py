#!/usr/bin/env python
# Author: 'JiaChen'


class ApiResponse(object):
    """回复客户端"""
    def __init__(self):
        self.response = {'code': None, 'message': None}
