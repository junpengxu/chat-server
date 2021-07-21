# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 1:08 上午
# @Author  : xu.junpeng

import json


class SerializeByte2Dict:
    def __init__(self):
        pass

    def loads(self, data: dict):
        """
        对message属性进行赋值
        :param data:
        :return:
        """
        attrs = self.__dict__.keys()
        for attr in attrs:
            setattr(self, attr, data.get(attr))

    def to_dict(self):
        data = {}
        for attr, value in self.__dict__:
            data[attr] = value
        return data

    def to_bytes(self):
        return json.dumps(self.to_dict()).encode("utf-8")
