######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
import numpy as np
from tools.updatedata import updatedata
from userchoose.userchoose import Userchoose


class Turtle4hour:
    """
    海龟交易策略,应用周期为4小时K线
    向上突破30根K线高点，空仓情况下做多，持有空单情况下反手做多；
    向下突破30根K线低点，空仓情况下做空，持有多单情况下反手做空；
    向上突破20根K线高点，持有空单情况下平空；
    向下突破20根K线低点，持有多单情况下平多；

    """

    def __init__(self, sid, pid, df, uid=None):
        """
        :param sid: 策略ID
        :param pid: 品种ID
        :param uid: 用户ID
        :param df: 初始化数据表用于后期计算（pandas DataFrame)
        """
        self.sid = sid
        self.pid = pid
        self.uid = uid
        self.df = df.iloc[-30 * 4 * 60:]
        self.position = 0

    def algorithm(self, ticker):
        """
        :param ticker: 订阅的数据
        :return:
        """
        price = np.float64(ticker['close'])
        high30 = self.df['high'].max()
        low30 = self.df['low'].min()
        df = self.df.iloc[-20 * 4 * 60]
        high20 = df['high'].max()
        low20 = df['low'].low()

        if price > high30:
            if self.position == 0:
                self.uid = Userchoose().choose(self.pid)
                self.position = 1
                self.price = price
            elif self.position == -1:
                self.position = 1
                self.price = price
        elif price < low30:
            if self.position == 0:
                self.uid = Userchoose().choose(self.pid)
                self.position = -1
                self.price = price
            elif self.position == 1:
                self.position = -1
                self.price = price

        elif price > high20:
            if self.position == -1:
                Userchoose().reset(self.uid, self.pid)
                self.position = 0
                self.price = price

        elif price < low20:
            if self.position == 1:
                Userchoose().reset(self.uid, self.pid)
                self.position = 0
                self.price = price

        else:
            pass

        self.df = updatedata(self.df, ticker)
