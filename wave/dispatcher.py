# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:28 上午
# @Author  : xu.junpeng
import threading
import time

from wave.utils.singleton import singleton


@singleton
class Dispatcher:
    def __init__(self, selector):
        """
        维护一个全局连接信息的map
        """
        self.selector = selector
        # self.user_broker_map = {"broker.user_id": broker}
        self.user_broker_map = {}
        # self.fd_broker_map = {"broker.fd": broker}
        self.fd_broker_map = {}

    def add_broker(self, broker):
        self.fd_broker_map[broker.fd] = broker

    def update_broker_user_info(self, broker):
        self.user_broker_map[broker.user_id] = broker

    def remove_broker(self, broker):
        if broker.user_id in self.user_broker_map:
            del self.user_broker_map[broker.user_id]
        if broker.fd in self.fd_broker_map:
            del self.fd_broker_map[broker.fd]
        self.selector.unregister(broker.conn)
        broker.close()

    def dispatch(self, fd):
        return self.fd_broker_map[fd]

    def dispatch_by_user_id(self, user_id):
        return self.user_broker_map.get(user_id)
