######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
from tools.indicator import ma, std
from tools import updatedata
from userchoose.userchoose import Userchoose


class Bollingerband:
    """
    布林带策略，采用一小时K线计算指标，周期为60小时
    向上突破上轨做多，向下突破中轨平多
    向下突破下轨做空，向上突破中轨平空

    """

    def __int__(self, sid, pid, df, uid=None):
        """
        BollingerBand 策略
        :param sid: 策略ID
        :param pid: 品种ID
        :param df: 初始化数据表用于后期计算（pandas DataFrame)
        :return:
        """
        self.sid = sid
        self.pid = pid
        self.uid = uid
        self.df = df.iloc[-60 * 60:]
        self.position = 0

    def algorithm(self, ticker):
        """
        布林带策略，应用周期一小时
        :param ticker: 订阅的数据
        :return:
        """
        mid = ma(self.df['close'], n=60 * 60)
        var = std(self.df['close'], n=60 * 60)
        upper = mid + 2 * var
        lower = mid - 2 * var
        price = float(ticker['close'])
        if (price > upper) and (self.position == 0):
            self.position = 1
            self.uid = Userchoose().choose(self.pid)
            # self.price = price
        elif (price < lower) and (self.position == 0):
            self.position = -1
            self.uid = Userchoose().choose(self.pid)
            # self.price = price
        elif (price < mid) and (self.position == 1):
            self.position = 0
            Userchoose().reset(self.uid, self.pid)
            # self.price = price
        elif (price > mid) and (self.position == -1):
            self.position = 0
            Userchoose().reset(self.uid, self.pid)
            # self.price = price
        else:
            pass
        # 更新分钟K线数据
        self.df = updatedata(self.df, ticker)
