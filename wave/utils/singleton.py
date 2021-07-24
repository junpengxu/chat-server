# -*- coding: utf-8 -*-
# @Time    : 2021/7/22 1:41 上午
# @Author  : xu.junpeng


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance
