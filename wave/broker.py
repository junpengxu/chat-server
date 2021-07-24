# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:12 上午
# @Author  : xu.junpeng
"""
使用broker来处理消息, 一个用户对应了一个borker
"""
import threading
import time
import json
import traceback

from wave.message import ConnFailMsg, Message, PingMsg, ConnSuccessMsg, TargetOfflineMsg, SendSuccessMsg, ConnectMsg
from wave.dispatcher import Dispatcher
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

    def write_msg_to_db(self, msg):
        print("write to db :", msg)

    def send(self, target_id, msg):
        target_broker = self.dispatcher.dispatch_by_user_id(target_id)
        if not target_broker:
            msg = TargetOfflineMsg()
            msg.target_id = target_id
            return self.response(msg.to_dict())
        # 是否判断target 数据成功发送出去呢
        target_broker.response(msg.to_dict())
        return self.response(SendSuccessMsg().to_dict())

    def process(self):
        # 数据装载不成功会抛出异常
        try:
            if not self.user_id:
                # 本次请求用来解析用户信息
                msg = self.recv().decode("utf-8")
                msg = ConnectMsg(json.loads(msg))
                self.online = True
                self.user_id = self.get_user_id_by_session_id(msg.session_id)
                self.dispatcher.update_broker_user_info(self)
                self.response(ConnSuccessMsg().to_dict())
            else:
                # 避免断开连接，接收到空的数据
                msg = json.loads(self.recv().decode("utf-8"))
                self.write_msg_to_db(msg)
                msg = Message(msg)
                if msg.end:
                    self.unregiste()
                else:
                    self.send(target_id=msg.target_id, msg=msg)
        except Exception as e:
            # 什么情况下，接收到的都是空呢，用户主动断开了。 但是server还在recv
            self.unregiste()
            print(traceback.format_exc())

    def recv(self):
        # 定义常量去替换
        return self.conn.recv(self.RECEIVE_NUMS)

    def close(self):
        try:
            self.conn.close()
        except Exception as e:
            print("重复关闭连接")
            print(traceback.format_exc())

    def unregiste(self):
        self.dispatcher.remove_broker(self)
        self.close()

    def response_connect(self):
        """
        响应连接
        :param msg: 要返回的信息
        :return:
        """
        if self.user_id:
            self.conn.sendall(ConnSuccessMsg().to_bytes())
        else:
            self.conn.sendall(ConnFailMsg().to_bytes())

    def response(self, msg):
        print("msg is ", msg)
        try:
            self.conn.sendall(Message(msg).to_bytes())
        except Exception as e:
            print(traceback.format_exc())

    def heart_beat(self):
        Thread(target=self._heart_beat).start()

    def _heart_beat(self):
        while True:
            try:
                # 用户主动断开连接，此处会抛出异常
                self.conn.sendall(PingMsg().to_bytes())
            except Exception as e:
                self.unregiste()
                break
            time.sleep(15)
        print("finish heart beat")
        return

    def destroy(self):
        pass

    def get_user_id_by_session_id(self, session_id):
        # user_id = int(self.redis_cli.get(session_id))
        if session_id == '123':
            return 1
        elif session_id == '456':
            return 2
        elif session_id == '789':
            return 3
        return 0
