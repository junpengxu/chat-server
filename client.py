# -*- coding: utf-8 -*-
# @Time    : 2021/7/3 7:29 下午
# @Author  : xu.junpeng
import time
import socket
import threading
import json
import traceback


class Client:
    def __init__(self, host, port):
        self.s = socket.socket()
        self.s.connect((host, port))

    def recv(self):
        while True:
            time.sleep(0.1)
            msg = self.s.recv(1024)
            print(msg)
            try:
                # 避免一次接收了两条数据
                print(json.loads(msg.decode()), "\n")
            except Exception as e:
                print(traceback.format_exc())

    def run(self):
        threading.Thread(target=self.recv).start()
        while True:
            input_msg = input("input >>>")
            if input_msg == '0':
                return
            elif input_msg == '1':
                self.s.sendall(b'{"session_id":"123", "target_id":2, "msg":"send to 2", "time":123}')
            elif input_msg == '2':
                self.s.sendall(b'{"session_id":"456", "target_id":1, "msg":"send to 1", "time":456}')
            elif input_msg == '3':
                self.s.sendall(b'{"session_id":"789", "target_id":1, "msg":"send to 3", "time":456}')

    def close(self):
        self.s.close()
if __name__ == '__main__':
    try:
        c = Client('127.0.0.1', 8000)
        c.run()
    except Exception as e:
        print("关闭连接")
        c.close()
