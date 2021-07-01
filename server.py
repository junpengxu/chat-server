# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng

import socket
import select


class Server(object):
    def __init__(self, host='127.0.0.1', port=8888, num=512):
        self.s = socket.socket()  # 创建套接字
        self.s.bind((host, port))  # 绑定端口
        self.s.listen(num)  # 开始监听，在拒绝链接之前，操作系统可以挂起的最大连接数据量，一般设置为5。超过后排队
        self.epoll_obj = select.epoll()
        self.epoll_obj.register(self.s, select.EPOLLIN)  # 把自己给注册了？
        self.connections = {}  # 保存socket与文件描述符的文件描述符
        self.user_fd = {}  # 保存user_id 与 文件描述符的关系

    def run(self):
        while True:
            events = self.epoll_obj.poll()  # 获取活跃事件，返回等待事件
            for fd, event in events:  # 遍历每一个活跃事件
                print(fd, event)
                if fd == self.s.fileno():  # 返回control fd的文件描述符。 # 其实这一步我一直没看懂.来一个新的连接，总会走到这一行
                    conn, addr = self.s.accept()  # 准备接收数据
                    self.connections[conn.fileno()] = conn  # 更新连接关系
                    self.epoll_obj.register(conn, select.EPOLLIN)  # 文件描述符注册如果已经存在，则会报错
                    msg = conn.recv(256)  # 前端限制长度
                    conn.sendall('ok'.encode())
                else:
                    try:
                        fd_obj = self.connections[fd]
                        msg = fd_obj.recv(200)
                        fd_obj.sendall('ok'.encode())
                    except BrokenPipeError:
                        self.epoll_obj.unregister(fd)
                        self.connections[fd].close()
                        del self.connections[fd]
        s.close()
        epoll_obj.close()

    def receive_msg(selfs, conn):
        pass

    def choose_target(self, user_id):
        pass

    def send_msg(self, conn, msg):
        pass

    def analyze_msg(self, msg):
        """
        return msg, img, target_id, uesr_id
        :param msg:
        :return:
        """

# https://www.cnblogs.com/leijiangtao/p/11819818.html

# 用户通过socket连接    user_id: socket
# 系统创建文件描述符     socket:fd
# 系统选择要把消息转发到那个用户   user_id:socket
