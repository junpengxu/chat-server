# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:28 上午
# @Author  : xu.junpeng
import traceback
from wave.utils.logger import base_log
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
        base_log.info("add broker:{}".format(broker.__repr__()))
        self.fd_broker_map[broker.fd] = broker

    def update_broker_user_info(self, broker):
        base_log.info("update_broker_user_info:{}".format(broker.__repr__()))
        self.user_broker_map[broker.user_id] = broker

    def remove_broker(self, broker):
        base_log.info("remove_broker:{}".format(broker.__repr__()))
        if broker.user_id in self.user_broker_map:
            del self.user_broker_map[broker.user_id]
        if broker.fd in self.fd_broker_map:
            del self.fd_broker_map[broker.fd]
        try:
            self.selector.unregister(broker.conn)
        except Exception as e:
            print("重复删除连接， unregiste")
            print(traceback.format_exc())
        broker.close()

    def dispatch(self, fd):
        return self.fd_broker_map[fd]

    def dispatch_by_user_id(self, user_id):
        return self.user_broker_map.get(user_id)
