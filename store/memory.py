# -*- coding: utf-8 -*-
# @Time    : 2021/7/13 1:26 上午
# @Author  : xu.junpeng
from multiprocessing import Queue


# TODO 使用代理模式
class Memory:
    def __init__(self, clean_user_queue_cnt=2048):
        self._user_fd_map = {}
        self._fd_conn_map = {}
        self.need_clean_user = Queue(clean_user_queue_cnt)

    @property
    def user_fd_map(self):
        return self._user_fd_map

    @property
    def fd_conn_map(self):
        return self._fd_conn_map

