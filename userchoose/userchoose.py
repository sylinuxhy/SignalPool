######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-

import redis
import numpy as np
from datetime import datetime
from pymongo import MongoClient


class Userchoose:
    """用户ID分配逻辑"""

    def __init__(self):
        """用户ID持仓数据保存到Redis数据库"""
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)
        self.col = MongoClient('localhost', 27017)['userschooserecord']['record']

    def choose(self, pid):
        """选择用户ID"""
        while True:
            try:
                uid = np.random.choice(100)
                if self.r.scard(uid) < 3 and not self.r.smembers(uid, pid):
                    self.r.sadd(uid, pid)
                    products = self.r.smembers(uid)
                    self.col.insert_one({uid: products, 'updatetime': datetime.now})
                    return uid
            except:
                continue

    def reset(self, uid, pid):
        self.r.srem(uid, pid)
        products = self.r.smembers(uid)
        self.col.insert_one({uid: products, 'updatetime': datetime.now})
