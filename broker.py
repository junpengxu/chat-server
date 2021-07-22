# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:12 上午
# @Author  : xu.junpeng
"""
使用broker来处理消息, 一个用户对应了一个borker
"""
import time

from message import ResponseMsg, Message
from dispatcher import Dispatcher
from threading import Thread


class Broker:
    """
    1. 每个broker接收自己的数据
    2. 每个broker可以响应自己的连接
    3. broker之间可以互相通信
    """
    RECEIVE_NUMS = 1024

    def __init__(self, user_id=None, fd=None, conn=None, online=False):
        self.user_id = user_id
        self.fd = fd
        self.conn = conn
        self.online = online
        self.dispatcher = Dispatcher()
        self.heart_beat()

    def send(self, target_id, msg):
        target_broker = self.dispatcher.dispatch_by_user_id(target_id)
        target_broker.response(msg.msg)

    def process(self):
        """
        1. 接受数据
        2. 解析数据
        3. 做出响应

        涉及到一个问题， 服务端是否可以需要根据用户端发送的断开连接的信号主动断开连接，这个断开链接的操作在哪里进行。断开连接之后Broker是否保留
        :return:
        """
        # 数据装载不成功会抛出异常
        msg = Message(self.recv())
        self.send(target_id=msg.target_id, msg=msg)

    def recv(self):
        # 定义常量去替换
        return self.conn.recv(self.RECEIVE_NUMS)

    def pull_msg(self):
        pass

    def registe(self):
        """
        把自己注册到全局的dispatcher中
        :param dispatcher:
        :return:
        """
        self.dispatcher.add_broker(self)
        self.response_connect()

    def unregiste(self):
        self.dispatcher.remove_broker(self)

    def response_connect(self):
        """
        响应连接
        :param msg: 要返回的信息
        :return:
        """
        if self.user_id:
            self.conn.sendall(ResponseMsg({"msg": "连接成功, 开始聊天吧"}))
        else:
            self.conn.sendall(ResponseMsg({"msg": "连接失败, 连接已断开"}))

    def response(self, msg):
        self.conn.sendall(Message(msg))

    def heart_beat(self):
        Thread(target=self._heart_beat).start()

    def _heart_beat(self):
        while True:
            try:
                self.conn.sendall(ResponseMsg({"msg": "ping"}))
            except Exception as e:
                self.unregiste()
                return
            time.sleep(10)

    def destroy(self):
        pass
