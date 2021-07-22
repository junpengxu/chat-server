# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 12:28 上午
# @Author  : xu.junpeng
from singleton import singleton


@singleton
class Dispatcher:
    def __init__(self):
        """
        维护一个全局连接信息的map
        """
        # broker_map = {"user_id":broker_instance}
        self.broker_map = {}
        # fd_map = {"fd":"user_id"}
        self.fd_map = {}

    def add_broker(self, broker):
        self.broker_map[broker.user_id] = broker
        self.fd_map[broker.fd] = broker.user_id

    def remove_broker(self, broker):
        user_id = broker.user_id
        del self.broker_map[user_id]
        fd = None
        for fd, _user_id in self.fd_map.items():
            if user_id == _user_id: break
        if fd is not None:
            del self.fd_map[fd]

    def dispatch(self, fd):
        """
        根据响应的fd，选对对应的broker开始执行后续处理逻辑
        如果拿不到broker要怎么处理呢?
        :param fd:
        :return:
        """
        return self.broker_map[self.fd_map[fd]]

    def dispatch_by_user_id(self, user_id):
        return self.broker_map[user_id]

    def session(self, session_id):
        """
        根据session_id 获取出userid
        :param session_id:
        :return: user_id
        """
        pass

    def destroy_broker(self):
        pass
