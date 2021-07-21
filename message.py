# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:36 上午
# @Author  : xu.junpeng
import json
from serializable import SerializeByte2Dict


class Message(SerializeByte2Dict):
    """
    需要考虑好垃圾回收， 服务端每接受到一个msg都会生成一个message对象
    """

    def __init__(self, msg: dict):
        """
        维护消息结构， 将读取到的消除处理成对应的结构
        """
        # self.session_id = None
        self.target_id = None
        self.timestamp = None
        self.msg = None
        self.img = None
        self.end = False
        self.loads(msg)

    # def __call__(self, msg=None, *args, **kwargs):
    #     self.loads(msg)


class ConnectMsg(SerializeByte2Dict):
    """
    用户首次连接socket的时候发送的信息
    """

    def __init__(self, msg):
        """
        维护消息结构， 将读取到的消除处理成对应的结构
        """
        self.session_id = None
        self.timestamp = None
        self.loads(msg)


class ResponseMsg(SerializeByte2Dict):
    """
    用户首次连接socket的时候发送的信息
    """

    def __init__(self, msg):
        """
        维护消息结构， 将读取到的消除处理成对应的结构
        """
        self.msg = None
        self.timestamp = None
        self.loads(msg)


msg = Message(
    b'{"target_id": 100002, "session_id": feoedd2321321, "msg": "发送给user_id为100002的用户", "img": "图片地址", "timestamp": 123321123}')