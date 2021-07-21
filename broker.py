# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:12 上午
# @Author  : xu.junpeng
"""
使用broker来处理消息, 一个用户对应了一个borker
"""
from message import ResponseMsg, Message
from dispatcher import Dispatcher


class Broker:
    def __init__(self, user_id=None, fd=None, conn=None, online=False):
        self.user_id = user_id
        self.fd = fd
        self.conn = conn
        self.online = online
        self.dispatcher = Dispatcher()

    def send(self, target_id, msg):
        target_broker = self.dispatcher.dispatch_by_user_id(target_id)
        target_broker.response(msg)

    def process(self):
        """
        1. 接受数据
        2. 解析数据
        3. 做出响应

        涉及到一个问题， 服务端是否可以需要根据用户端发送的断开连接的信号主动断开连接，这个断开链接的操作在哪里进行。断开连接之后Broker是否保留
        :return:
        """
        # 数据装载不成功会抛出异常
        msg = self.recv(1024)
        msg = Message(msg)
        self.send(target_id=msg.target_id, msg=msg.msg)

    def recv(self):
        # 定义常量去替换
        return self.conn.recv(1024)

    def pull_msg(self):
        pass

    def register(self):
        """
        把自己注册到全局的dispatcher中
        :param dispatcher:
        :return:
        """
        self.dispatcher.add_broker(self)

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
