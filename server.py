# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng
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


class ChatServer(object):
    RECEIVE_NUMS = 1024

    def __init__(self, host='127.0.0.1', port=8888, num=1):
        self.redis_cli = redis.StrictRedis(host='localhost', port=6379, db=15, decode_responses=True)
        self.s = socket.socket()  # 创建套接字
        self.s.bind((host, port))  # 绑定端口
        self.s.listen(num)  # 开始监听，在拒绝链接之前，操作系统可以挂起的最大连接数据量，一般设置为5。超过后排队
        self.epoll_obj = select.epoll()  # 使用epoll模型
        self.epoll_obj.register(self.s, select.EPOLLIN)  # 把自己给注册了？
        self.broker = Memory()
        self.dispatcher = Dispatcher()

    @staticmethod
    def receive_msg(conn):
        return conn.recv(ChatServer.RECEIVE_NUMS)

    def register(self, conn):
        self.register_conn_to_epoll(conn)
        broker = Broker(conn=conn)
        try:
            msg = json.loads(self.receive_msg(conn).decode("utf-8"))
            msg = ConnectMsg(msg)
            user_id = self.get_user_id_by_session_id(msg.session_id)
            broker.user_id = user_id
            broker.fd = conn.fileno()
            broker.online = True
        except Exception as e:
            print(traceback.format_exc())
            print("register fail")
        return broker

    def register_conn_to_epoll(self, conn):
        self.epoll_obj.register(conn, select.EPOLLIN)  # 文件描述符注册如果已经存在，则会报错

    def get_user_id_by_session_id(self, session_id):
        user_id = int(self.redis_cli.get(session_id))
        return user_id

    def run(self):
        while True:
            events = self.epoll_obj.poll(10)  # 获取活跃事件，返回等待事件
            for fd, event in events:  # 遍历每一个活跃事件
                if fd == self.s.fileno():  # 返回control fd的文件描述符。 # 其实这一步我一直没看懂.来一个新的连接，总会走到这一行
                    # 第一次连接，会走到这一行。需要携带自己的信息，才能注册成功
                    conn, addr = self.s.accept()  # 获取连接的socket
                    broker = self.register(conn)  # 如果是连接不成功的user, 应该是要被垃圾回收的
                    broker.registe()  # 把自己注册到dispatcher中
                else:
                    try:
                        broker = self.dispatcher.dispatch(fd)
                        broker.process()
                    except Exception:
                        print(traceback.format_exc())
                        self.epoll_obj.unregister(fd)

if __name__ == '__main__':
    a = ChatServer(port=8529)
    a.run()
