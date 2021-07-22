# -*- coding: utf-8 -*-
# @Time    : 2021/7/22 1:41 上午
# @Author  : xu.junpeng

def singleton(cls, *args, **kw):
    instance = {}

    def _singleton():
        if cls not in instance:
            instance[cls] = cls(*args, **kw)
        return instance[cls]

    return _singleton
