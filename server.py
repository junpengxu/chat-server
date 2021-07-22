# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng
import json
import redis
import socket
import select
import traceback
from store.memory import Memory
from message import ConnectMsg
from broker import Broker
from dispatcher import Dispatcher


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
        # TODO 这里默认每个聊天的消息长度都在1024个字节一下
        return conn.recv(ChatServer.RECEIVE_NUMS)

    def register(self, conn):
        # 默认首次连接，数据中要携带session, 以此分配broker
        # 如果数据非法, 则不执行注册操作, 并且关闭连接。这部分代码只有首次连接到server的时候才会进入。如果这里信息解析失败，是没有办法再次解析的
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
                        # 选择broker, 如果是client关闭了，这里会输出空数据
                        broker = self.dispatcher.dispatch(fd)
                        broker.process()
                    except Exception:
                        # 找不到这个fd的连接信息，这个fd不是首次连接，但是维护的连接信息中找不到。一般是服务有问题，并且是严重问题
                        # 需要对出问题的环节做处理
                        # 目前先断开连接
                        # client断开连接后， 要从epoll中删除
                        print(traceback.format_exc())
                        # 从 epoll中删除连接
                        self.epoll_obj.unregister(fd)
                        # 把 socket 关闭


a = ChatServer(port=8529)
a.run()
