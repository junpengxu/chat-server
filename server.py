# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng
import json
import redis
import socket
import select
from typing import Tuple
import traceback
from heart_beat import HeartBeat
from threading import Thread
from store.memory import Memory


# TODO client 端主动断开连接，server会抛出异常
# Expecting value: line 1 column 1 (char 0)
# local variable 'user_id' referenced before assignment

class ChatServer(object):
    RECEIVE_NUMS = 1024

    def __init__(self, host='127.0.0.1', port=8888, num=1):
        self.redis_cli = redis.StrictRedis(host='localhost', port=6379, db=15, decode_responses=True)
        self.s = socket.socket()  # 创建套接字
        self.s.bind((host, port))  # 绑定端口
        self.s.listen(num)  # 开始监听，在拒绝链接之前，操作系统可以挂起的最大连接数据量，一般设置为5。超过后排队
        # self.epoll_obj = select.epoll()  # 使用epoll模型
        self.epoll_obj = select.epoll()  # 使用epoll模型
        self.epoll_obj.register(self.s, select.EPOLLIN)  # 把自己给注册了？
        self.receive_nums = 1024
        self.broker = Memory()
        self.user_fd_map = self.broker.user_fd_map
        self.fd_conn_map = self.broker.fd_conn_map
        self.need_clean_user = self.broker.need_clean_user
        self.listen_new_user_conn()
        self.heart_beat()
        self.clean_user()

    def listen_new_user_conn(self):
        """
        有新用户连接进来后，仅执行一次，检查是否有未读消息。如果有，遍历消息发送给用户
        :return:
        """
        pass


    def heart_beat(self):
        hb = HeartBeat(self.user_fd_map, self.fd_conn_map, self.need_clean_user)
        t = Thread(target=hb.run)
        t.start()

    def clean_user(self):
        def clean_user():
            while True:
                try:
                    # 这段代码，基本不会被走到，因为通过心跳检测发现用户离开了，比较慢
                    # 第二点，用户离开后但是本地还没有断开文件描述符，会一直接收到空数据，继而触发后续清理操作
                    user = self.need_clean_user.get()
                    print("clean user:{} now".format(user))
                    self.unregister_by_user(user)
                    print("clean user:{} sucess".format(user))
                except Exception as e:
                    print("clear user raise exception: {}".format(traceback.format_exc()))
        t = Thread(target=clean_user)
        t.start()

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
                        self.send_msg(json.dumps({"msg": "please break connect"}), conn)
                        self.close_conn(fd)
                    except Exception as e:
                        print(e)

    def unregister_by_user(self, user):
        fd = self.user_fd_map[user]
        del self.user_fd_map[user]
        self.close_conn(fd)

    def unregister_by_fd(self, fd):
        try:
            for user, _fd in self.user_fd_map.items():
                if fd == _fd: break
            del self.user_fd_map[user]
            self.close_conn(fd)
        except Exception as e:
            print("unregister_by_fd raise error", traceback.print_exc())

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
            self.update_fd_and_conn_map(conn.fileno(), conn)
            self.update_user_and_fd_map(user_id, conn.fileno())
            self.send_msg(json.dumps({"msg": "connect success"}), conn)
            print("registe user:{} success".format(user_id))

    def response(self, fd):
        conn = self.get_conn_by_fd(fd)
        msg = self.receive_msg(conn)
        if not msg:
            print("receive empty, may be user close conn")
            self.unregister_by_fd(fd)
            return
        user_id, target_id, msg, end = self.analyse_msg(msg)
        if end:
            self.send_msg(json.dumps({"msg": msg}), conn)
            self.close_conn(fd)
        else:
            target_conn = self.get_conn_by_user_id(target_id)
            self.send_msg(json.dumps({"user_id": user_id, "msg": msg}), target_conn)
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

    def update_fd_and_conn_map(self, fd, socket):
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
        # TODO 用户主动断开连接后，这里会出现异常
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

    def analyse_msg(self, msg: bytes) -> Tuple[int, int, str, bool]:
        try:
            data = json.loads(msg.decode(encoding="utf-8"))
            user_id = int(self.redis_cli.get(data["session_id"]))
            target_id = data["target_id"]
            msg = data["msg"]
            end = data["end"]
            # img = msg.get("img")
        except Exception as e:
            print(traceback.format_exc())
            target_id = 0
            msg = "消息解析失败，会话关闭"
            user_id = 0
            end = 1  # 直接结束会话
        if end:
            msg = "连接已经断开"
        return user_id, target_id, msg, end

    @staticmethod
    def send_msg(msg: str, conn):
        conn.sendall(msg.encode(encoding="utf-8"))


a = ChatServer(port=8529)
a.run()
