# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng
import sys
import threading

sys.path.append('/opt/project/venv')

# import gevent
# from gevent import monkey
# monkey.patch_all()
# from gevent import pool as gevent_pool

import json
import redis
import socket
import select
import parser
import traceback
from wave.store.memory import Memory
from wave.message import ConnectMsg
from wave.broker import Broker
from wave.dispatcher import Dispatcher
from concurrent.futures import ThreadPoolExecutor

class ChatServer(object):
    RECEIVE_NUMS = 1024

    def __init__(self, host='127.0.0.1', port=8888, num=256):
        # self.redis_cli = redis.StrictRedis(host='localhost', port=6379, db=15, decode_responses=True)
        self.s = socket.socket()  # 创建套接字
        self.s.bind((host, port))  # 绑定端口
        self.s.listen(num)  # 开始监听，在拒绝链接之前，操作系统可以挂起的最大连接数据量，一般设置为5。超过后排队
        self.s.setblocking(False)
        self.epoll_obj = select.epoll()  # 使用epoll模型
        self.epoll_obj.register(self.s.fileno(), select.EPOLLIN)  # 把自己给注册了？
        self.broker = Memory()
        self.dispatcher = Dispatcher(self.epoll_obj)
        # self.pool = gevent_pool.Pool(1024)
        self.pool = ThreadPoolExecutor(256)

    @staticmethod
    def receive_msg(conn):
        return conn.recv(ChatServer.RECEIVE_NUMS)

    def register(self, conn):
        broker = Broker(conn=conn)
        try:
            msg = json.loads(self.receive_msg(conn).decode("utf-8"))
            user_id = self.get_user_id_by_session_id(msg['session_id'])
            broker.user_id = user_id
            broker.fd = conn.fileno()
            broker.online = True
        except Exception as e:
            print(traceback.format_exc())
            print("register fail")
        return broker

    def register_conn_to_epoll(self, conn):
        self.epoll_obj.register(conn.fileno(), select.EPOLLIN | select.EPOLLET)
        # self.epoll_obj.register(conn, select.EPOLLIN)  # 文件描述符注册如果已经存在，则会报错, 这样注册，epoll不停的在响应

    def get_user_id_by_session_id(self, session_id):
        # user_id = int(self.redis_cli.get(session_id))
        if session_id == '123':
            return 1
        elif session_id == '456':
            return 2
        elif session_id == '789':
            return 3
        return 0



    def handle(self, fd):
        if fd == self.s.fileno():  # 返回control fd的文件描述符。 # 其实这一步我一直没看懂.来一个新的连接，总会走到这一行
            # 第一次连接，会走到这一行。需要携带自己的信息，才能注册成功
            conn, addr = self.s.accept()  # 获取连接的socket
            broker = self.register(conn)  # 如果是连接不成功的user, 应该是要被垃圾回收的
            self.dispatcher.add_broker(broker=broker)
            broker.response_connect()
            print("注册成功 broker is", broker.__dict__)
        else:
            try:
                broker = self.dispatcher.dispatch(fd)
                print("接收成功，broker is", broker.__dict__)
                broker.process()
                print("启动结束")
                pass
            # broker.process()
            except Exception:
                print(traceback.format_exc())
                self.epoll_obj.unregister(fd)

    def run(self):
        while True:
            events = self.epoll_obj.poll(timeout=1)  # 获取活跃事件，返回等待事件
            for fd, event in events:  # 遍历每一个活跃事件
                # gevent.spawn(self.handle, fd).join()
                print("pre handle")
                self.handle(fd)
                print("end handle")

if __name__ == '__main__':
    a = ChatServer(port=8000)
    a.run()


# TODO 这一版有问题。 会阻塞在recv阶段，有空了再debug