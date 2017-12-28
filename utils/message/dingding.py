from .base import BaseMessage
class DingDing(BaseMessage):
    """丁丁发送"""
    def __init__(self):
        pass

    def send(self,subject,body,to,name):
        print('钉钉消息发送成功')