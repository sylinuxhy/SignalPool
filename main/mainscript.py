######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
import json
import threading
import pandas as pd
from kafka import KafkaConsumer
from pymongo import MongoClient
from multiprocessing import Process
from datetime import datetime, timedelta
from algorithm.ma import Ma
from algorithm.rsi import Rsi
from algorithm.cci import Cci
from algorithm.kdj import Kdj
from algorithm.macd import Macd
from algorithm.rbreakdaily import Rbreakday
from algorithm.rbreakweekly import Rbreakweek
from algorithm.turtle4hour import Turtle4hour
from algorithm.turtle2hour import Turtle2hour
from algorithm.bollingerband import Bollingerband


class Main:
    """
    主程序，用来分主题运行策略池，方便管理维护
    """

    def __init__(self, sub, db='websocket1mindata',
                 strategies=(Bollingerband, Cci, Kdj, Ma, Macd, Rbreakday,
                             Rbreakweek, Rsi, Turtle4hour, Turtle2hour)):
        """
        :param sub: 订阅主题
        :param db: MongoDB 数据库名称
        :param strategies: 策略（多个策略）
        """

        self.db = db
        self.subscribe = sub
        self.strategy_pool = strategies
        self.col = MongoClient('localhost', 27017)[self.db][self.subscribe]
        self.consumer = KafkaConsumer(self.subscribe, bootstrap_servers='kafka-28:9092',
                                      value_deserializer=lambda v: json.loads(v.decode('utf-8')))
        self.df = pd.DataFrame(list(self.col.find({'_id': 0, 'open': 1, 'high': 1, 'low': 1, 'close': 1, 'time': 1},
                                                  {'$gte': datetime.now(),
                                                   '$lt': (datetime.now() - timedelta(days=30))})))
        self.df = self.df.apply(pd.to_numeric(errors='ignore'))

    def run(self):
        """运行策略池的策略"""
        # 初始化策略池中的策略
        strategy_pool = []
        for i, strategy in enumerate(self.strategy_pool):
            strategy_pool.append(strategy(i, self.subscribe, self.df))
        # 多进程运行策略池
        for msg in self.consumer:
            ticker = msg.value
            for strategy in strategy_pool:
                p = Process(target=strategy.algorithm, args=(ticker,))
                p.start()


if __name__ == "__main__":
    # 订阅的主题
    subscribes = ['1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009']
    # 初始化每个主题下的主程序
    top_controller = []
    for subscribe in subscribes:
        top_controller.append(Main(subscribe))
    # 多线程方式启动每个主题下的主程序
    for topic_group in top_controller:
        threading.Thread(target=topic_group, daemon=True).start()
