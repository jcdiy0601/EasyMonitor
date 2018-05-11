#!/usr/bin/env python
# Author: 'JiaChen'


class ApiResponse(object):
    """回复客户端"""
    def __init__(self):
        self.code = None
        self.message = None
        self.data = {}
