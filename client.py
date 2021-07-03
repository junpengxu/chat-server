# -*- coding: utf-8 -*-
# @Time    : 2021/7/3 7:29 下午
# @Author  : xu.junpeng
import time
import socket
import threading


class Client:
    def __init__(self, host, port):
        self.s = socket.socket()
        self.s.connect((host, port))

    def recv(self):
        while True:
            print("recving")
            time.sleep(1)
            msg = self.s.recv(1024)
            print("\n" * 3)
            print("=====================")
            print(msg.decode())
            print("=====================")

    def run(self):
        threading.Thread(target=self.recv).start()
        while True:
            input_msg = input("input >>>")
            if input_msg == '0':
                return
            self.s.sendall(input_msg.encode())


c = Client('127.0.0.1', 8010)
c.run()
