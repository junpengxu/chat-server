# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:36 上午
# @Author  : xu.junpeng
import time
from wave.utils.serializable import SerializeByte2Dict


class Message(SerializeByte2Dict):
    """
    需要考虑好垃圾回收， 服务端每接受到一个msg都会生成一个message对象
    """

    def __init__(self, msg: dict):
        """
        维护消息结构， 将读取到的消除处理成对应的结构
        """
        # self.session_id = None
        super().__init__()
        self.target_id = None
        self.timestamp = time.time()
        self.msg = None
        self.img = None
        self.end = False
        self.loads(msg)

    # def __call__(self, msg=None, *args, **kwargs):
    #     self.loads(msg)


class ConnectMsg(Message):
    """
    用户首次连接socket的时候发送的信息
    """

    def __init__(self, msg):
        """
        维护消息结构， 将读取到的消除处理成对应的结构
        """
        self.session_id = None
        self.timestamp = time.time()
        self.loads(msg)


class PingMsg(Message):

    def __init__(self):
        self.msg = "ping"
        self.timestamp = time.time()


class ResponseMsg(Message):
    """
    用户首次连接socket的时候发送的信息
    """

    def __init__(self, msg=None):
        """
        维护消息结构， 将读取到的消除处理成对应的结构
        """
        if msg is None:
            msg = {}
        self.msg = None
        self.timestamp = time.time()
        self.loads(msg)


class ConnSuccessMsg(Message):

    def __init__(self):
        self.msg = "连接成功，开始聊天吧"
        self.timestamp = time.time()


class ConnFailMsg(Message):

    def __init__(self):
        self.msg = "连接失败, 连接已断开"
        self.timestamp = time.time()


class TargetOfflineMsg(Message):

    def __init__(self):
        self.msg = "对方不在线"
        self.timestamp = time.time()


class SendSuccessMsg(Message):

    def __init__(self):
        self.msg = "发送成功"
        self.timestamp = time.time()


if __name__ == '__main__':
    ResponseMsg({"msg": "连接失败, 连接已断开"}).to_bytes()
