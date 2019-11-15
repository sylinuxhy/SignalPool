######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-

import websocket
import json
import time
import zlib
import _thread
from kafka import KafkaProducer


def deflate(data):
    """
    :param data: zip数据
    :return: 解压后的数据
    """
    try:
        return zlib.decompress(data, -zlib.MAX_WBITS).decode('utf8')
    except zlib.error:
        return zlib.decompress(data).decode('utf8')


class MySock:
    """
    定制化的58coin Socket接口
    """

    def __init__(self):
        """
        : socket订阅信息

        """
        stream = '1001@kline_1min/1002@kline_1min/1003@kline_1min/1004@kline_1min/1005@kline_1min/' \
                 '1006@kline_1min/1007@kline_1min/1008@kline_1min/1009@kline_1min'
        wss = 'wss://openws.58ex.com/v1/stream?streams={}'.format(stream)
        self.producer = KafkaProducer(bootstrap_servers='kafka-28:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.header = {'Content-Type': 'application/json'}
        self.ws = websocket.WebSocketApp(wss, header=self.header, on_message=self.on_message,
                                         on_error=self.on_error, on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever()

    def on_open(self):
        """Socket数据订阅"""

        _thread.start_new_thread(self.heartbeat, (1,))

    def heartbeat(self, a):
        while True:
            req = '{"event":"ping"}'
            print(req)
            self.ws.send(req)
            time.sleep(60)

    def on_message(self, message):
        """Socket数据接收"""
        recv = json.loads(deflate(message))
        # print(recv)
        if recv and recv['product']:
            topic = recv['product']
            data = recv['data']
            print(data)
            self.producer.send(topic, data)

    def on_error(self, error):
        """socket错误原因"""
        print(error)

    def on_close(self):
        """Socket链接关闭"""
        print('链接关闭 ……')

    def process(self, recv):
        """具体数据处理逻辑模块"""
        print('此方法需定制化实现')


if __name__ == '__main__':
    while True:
        try:
            MySock()
            break
        except:
            continue
