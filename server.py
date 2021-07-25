# -*- coding: utf-8 -*-
# @Time    : 2021/7/1 10:53 下午
# @Author  : xu.junpeng
import sys

sys.path.append('/opt/project/venv')
import socket
import selectors

from wave.broker import Broker
from wave.dispatcher import Dispatcher

from wave.utils.logger import base_log

class ChatServerV2:
    def __init__(self, host='0.0.0.0', port=12345, num=256):
        self.s = socket.socket()
        self.s.bind((host, port))
        self.s.listen(num)
        self.s.setblocking(False)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.s, selectors.EVENT_READ, self.accept)
        self.dispatcher = Dispatcher(self.selector)

    def accept(self, sock, mask):
        conn, addr = sock.accept()  # Should be ready
        conn.setblocking(False)
        broker = Broker(fd=conn.fileno(), conn=conn)
        self.dispatcher.add_broker(broker=broker)
        broker.response_connect()
        self.selector.register(conn, selectors.EVENT_READ, self.read)

    def read(self, conn, mask):
        try:
            broker = self.dispatcher.dispatch(conn.fileno())
            broker.process()
        except Exception as e:
            self.dispatcher.remove_broker(self.dispatcher.dispatch(conn.fileno()))

    def run(self):
        base_log.info("server running")
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def close(self):
        print("do close")
        self.s.close()


if __name__ == '__main__':
    a = ChatServerV2(port=12345)
    try:
        a.run()
    except Exception as e:
        a.close()
