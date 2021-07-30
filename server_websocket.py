import json
from datetime import datetime
import redis
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from wave.utils.logger import base_log

class Server(WebSocket):

    def __init__(self, server, sock, address):
        self.user_instance_map = {}  # 保存用户id与对象
        self.address_user_map = {}  # 保存连接fd与用户id
        self.unread_prefix = "UNREAD"
        self.redis_cli = redis.StrictRedis(db=15, decode_responses=True)
        super().__init__(server, sock, address)

    def handleMessage(self):
        # echo message back to client
        """
            {
                "target_id":123,    # 发送到那个用户
                "msg":"hi",         # 发送消息
            }
        """
        try:
            # 加载数据
            base_log.info("msg is: {}".format(self.data))
            data = json.loads(self.data)
            # 选择发送方
            target_id = data.get("target_id")
            # 解析消息
            msg = data.get("msg")
            _time = data.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # 选择接收方
            target = self.user_instance_map.get(target_id)
            latter = {
                "msg": msg,
                "time": _time,
                "user_id": self.address_user_map[self.address],  # 从哪个用户发来的消息
            }
            latter = json.dumps(latter)
            if not target:
                return self.send_unread_msg(target_id, latter)
            # 组装消息，要带上发送方用户id
            # 发送
            target.sendMessage(latter)
        except Exception as e:
            print(e)

    def send_unread_msg(self, user_id, msg):
        self.redis_cli.rpush(self.unread_prefix + "-" + str(user_id), msg)

    def handleConnected(self):
        self.sendMessage("连接成功")
        self.registe_user()

    def get_token(self, headers=[]):
        for (key, value) in headers:
            if key == "token":
                return value
        base_log.info("token not found, address is {}".format(self.address))
        return ""

    def get_user_id(self):
        return self.redis_cli.get(self.get_token(self.request.headers._headers))

    def get_history_msg(self, user_id):
        msgs = []
        while True:
            msg = self.redis_cli.lpop(self.unread_prefix + str(user_id))
            # msg 是json.dumps 之后的字符串
            if msg:
                print("unread msg: ", msg)
                msgs.append(msg)
            else:
                break
        return msgs

    def registe_user(self):
        # 首次连接后，注册个人信息
        user_id = self.get_user_id()
        base_log.info("registe uesr: {}".format(user_id))
        if user_id:
            self.user_instance_map[user_id] = self
            self.address_user_map[self.address] = user_id
        else:
            # 用户信息不正确, 断开连接
            return self.handleClose()
        history_msgs = self.get_history_msg(user_id)
        base_log.info("user:{} history msg is {}".format(user_id, history_msgs))
        self.sendMessage(history_msgs)

    def handleClose(self):
        user_id = self.address_user_map.get(self.address)
        if user_id:
            del self.address_user_map[self.address]
        if self.user_instance_map.get(user_id):
            del self.user_instance_map[user_id]
        base_log.info("close user: {}".format(user_id))


if __name__ == '__main__':
    server = SimpleWebSocketServer('', 12345, Server)
    server.serveforever()
