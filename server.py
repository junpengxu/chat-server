# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng
import json
import socket
import select
from typing import Tuple


# TODO client 端主动断开连接，server会抛出异常
# Expecting value: line 1 column 1 (char 0)
# local variable 'user_id' referenced before assignment

class ChatServer(object):
    RECEIVE_NUMS = 1024

    def __init__(self, host='127.0.0.1', port=8888, num=1):
        self.s = socket.socket()  # 创建套接字
        self.s.bind((host, port))  # 绑定端口
        self.s.listen(num)  # 开始监听，在拒绝链接之前，操作系统可以挂起的最大连接数据量，一般设置为5。超过后排队
        self.epoll_obj = select.epoll()  # 使用epoll模型
        self.epoll_obj.register(self.s, select.EPOLLIN)  # 把自己给注册了？
        self.user_fd_map = {}
        self.fd_conn_map = {}
        self.receive_nums = 1024

    def run(self):
        while True:
            events = self.epoll_obj.poll(10)  # 获取活跃事件，返回等待事件
            for fd, event in events:  # 遍历每一个活跃事件
                if fd == self.s.fileno():  # 返回control fd的文件描述符。 # 其实这一步我一直没看懂.来一个新的连接，总会走到这一行
                    # 第一次连接，会走到这一行。需要携带自己的信息，才能注册成功
                    conn, addr = self.s.accept()  # 获取连接的socket
                    self.register(conn)
                else:
                    try:
                        self.response(fd)  # 这里就是具体的socket对应的文件描述符
                    except BrokenPipeError:
                        self.send_msg("please break connect", conn)
                        self.close_conn(fd)
                    except Exception as e:
                        print(e)

    def close_conn(self, fd):
        self.unregister_conn_from_epoll(fd)
        self.close_socekt(self.get_conn_by_fd(fd))
        self.del_fd_from_fd_and_socket_map(fd)

    def register(self, conn):
        # 首次获取到足够的信息后才能继续向下注册
        msg = self.receive_msg(conn)
        user_id, _, _, end = self.analyse_msg(msg)
        if not end:
            self.register_conn_to_epoll(conn)
            self.update_fd_and_socket_map(conn.fileno(), conn)
            self.update_user_and_fd_map(user_id, conn.fileno())
            self.send_msg("connect success", conn)
            print("registe user:{} success".format(user_id))

    def response(self, fd):
        conn = self.get_conn_by_fd(fd)
        msg = self.receive_msg(conn)
        user_id, target_id, msg, end = self.analyse_msg(msg)
        if end:
            self.send_msg(msg, conn)
            self.close_conn(fd)
        else:
            target_conn = self.get_conn_by_user_id(target_id)
            self.send_msg(msg, target_conn)
            print("user:{} send msg:{} to user:{}".format(user_id, msg, target_id))

    @staticmethod
    def receive_msg(conn):
        # TODO 这里默认每个聊天的消息长度都在1024个字节一下
        return conn.recv(ChatServer.RECEIVE_NUMS)

    def register_conn_to_epoll(self, conn):
        self.epoll_obj.register(conn, select.EPOLLIN)  # 文件描述符注册如果已经存在，则会报错

    def unregister_conn_from_epoll(self, fd):
        self.epoll_obj.unregister(fd)

    def get_events(self):
        return self.epoll_obj.poll()

    def update_user_and_fd_map(self, user_id, fd):
        """
        更新用户与文件描述符号的关系
        :param user_id: user id
        :param fd: file distribute
        :return: NOne
        """
        if self.user_fd_map.get(user_id):
            print("fd exist, it may be a error, fd is {}, origin user_id is {}".format(
                self.user_fd_map[user_id], user_id)
            )
        self.user_fd_map[user_id] = fd

    def update_fd_and_socket_map(self, fd, socket):
        """
        更新文件描述符号与具体的socket连接
        :return:
        """
        if self.fd_conn_map.get(fd):
            print("fd exist, it may be a error, fd is {}".format(fd))
        self.fd_conn_map[fd] = socket

    def del_fd_from_fd_and_socket_map(self, fd):
        del self.fd_conn_map[fd]

    def get_conn_by_fd(self, fd):
        """
        根据文件描述符号获取具体的socket
        :return:
        """
        return self.fd_conn_map[fd]

    def get_conn_by_user_id(self, user_id):
        """
        根据用户id获取出此用户的socket连接
        :param user_id:
        :return:
        """
        fd = self.user_fd_map.get(user_id)
        if not fd: raise Exception("can not found user connect")
        conn = self.fd_conn_map.get(fd)
        if not conn: raise Exception("can not found fd:{}'s socket".format(fd))
        return conn

    def close_socekt(self, conn):
        conn.close()

    def close_server(self):
        self.s.close()

    @staticmethod
    def analyse_msg(msg: bytes) -> Tuple[int, int, str, bool]:
        try:
            data = json.loads(msg.decode(encoding="utf-8"))
            print(msg)
            user_id = data["user_id"]
            target_id = data["target_id"]
            msg = data["msg"]
            end = data["end"]
            # img = msg.get("img")
        except Exception as e:
            print(e)
            target_id = user_id
            msg = "消息解析失败，会话关闭"
            user_id = user_id
            end = 0
        if end: msg = "连接已经断开"
        return user_id, target_id, msg, end

    @staticmethod
    def send_msg(msg: str, conn):
        conn.sendall(msg.encode(encoding="utf-8"))


a = ChatServer(port=8529)
a.run()
