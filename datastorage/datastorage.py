######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
import json
from datetime import datetime
from pymongo import MongoClient
from kafka import KafkaConsumer


class DataStorage:
    """
    该类，主要将订阅的数据按订阅主题分别存储到MongoDB数据库中
    """
    def __init__(self, subscribe):
        """

        :param subscribe: 订阅的主题
        """
        db = 'websocket1mindata'
        self.subscribe = subscribe
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db]
        self.consumer = KafkaConsumer(bootstrap_servers='kafka-28:9092',
                                      value_deserializer=lambda v: json.loads(v.decode('utf-8')))
        self.consumer.subscribe(self.subscribe)

    def update(self):
        """
        按消费者获取到的主题分别存储数据
        :return:
        """
        for msg in self.consumer:
            col = msg.topic
            data = msg.value
            data['time'] = datetime.fromtimestamp(float(data['time']) / 1000)
            self.db[col].update_one({'time': data['time']}, {'$set': data}, upsert=True)
            print('update data,{}'.format(data))


if __name__ == '__main__':
    DataStorage(['1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009']).update()
