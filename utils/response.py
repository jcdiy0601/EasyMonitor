#!/usr/bin/env python
# Author: 'JiaChen'


class BaseResponse(object):
    """响应基类"""
    def __init__(self):
        self.status = True
        self.message = None
        self.error = None
        self.data = None
