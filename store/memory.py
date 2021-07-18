# -*- coding: utf-8 -*-
# @Time    : 2021/7/13 1:26 上午
# @Author  : xu.junpeng
from multiprocessing import Queue

# TODO 使用代理模式
class Memory:
    def __init__(self, clean_user_queue_cnt=2048):
        self.user_fd_map = {}
        self.fd_conn_map = {}
        self.need_clean_user = Queue(2048)

    def update(self):
        pass

    def remove(self):
        pass

    def gen_user_fd_map(self):
        pass

    def gen_fe_conn_map(self):
        pass

    def gen_clean_user_queue(self):
        pass
