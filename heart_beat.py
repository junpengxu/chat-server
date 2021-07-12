# -*- coding: utf-8 -*-
# @Time    : 2021/7/12 8:49 下午
# @Author  : xu.junpeng
import time
import traceback

class HeartBeat:
    def __init__(self, user_fd_map, fd_conn_map, unregisgter_user):
        self.user_fd_map = user_fd_map
        self.fd_conn_map = fd_conn_map
        self.unregisgter_user = unregisgter_user
        self.user_check_time_map = {}  # 保存用户被检查的时间
        self.check_interview = 10

    def scan(self):
        while True:
            time.sleep(5)
            # 应该每个用户在固定的轮训期间内被发送心跳检测。
            # 用户主动上报心跳
            print('user_fd_map', self.user_fd_map)
            print("fd_conn_map", self.fd_conn_map)
            user_list = list(self.user_fd_map.keys())
            for user in user_list:
                user_conn = self.fd_conn_map.get(self.user_fd_map[user], None)
                if not user_conn: self.unregisgter_user.put(user)
                try:
                    # 十秒轮训一次
                    if user not in self.user_check_time_map or self.user_check_time_map[
                        user] + self.check_interview < time.time():
                        self.ping(user_conn)
                        self.user_check_time_map[user] = time.time()
                except BrokenPipeError:
                    print("用户主动断开连接")
                    self.unregisgter_user.put(user)
                except Exception as e:
                    print("心跳出现异常")
                    print(traceback.format_exc())
                    self.unregisgter_user.put(user)

    def ping(self, conn):
        conn.sendall("ping".encode(encoding="utf-8"))

    def run(self):
        self.scan()
