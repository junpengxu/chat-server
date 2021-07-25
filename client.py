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
                self.s.sendall(b'{"session_id":"MTY1ODMyOTA2Mi45Mjc4NzQ2OjViODBkYmFhNjE4OTg5MzQ2NmZiYmRlNDViYWZjYjgzNDU1MDZkODc=", "target_id":2, "msg":"send to 2"}')
            elif input_msg == '2':
                self.s.sendall(b'{"session_id":"MTY1ODMyOTY5OS45MDM3NDExOmIzMWQ2YzVhYzlmMjE4MzhkNmIyNDhjN2E5ZTViZDAxNDQwNjkyNGE=", "target_id":1, "msg":"send to 1"}')


    def close(self):
        self.s.close()
if __name__ == '__main__':
    c = Client('127.0.0.1', 12345)
    try:
        c.run()
    except Exception as e:
        print("关闭连接")
        c.close()
