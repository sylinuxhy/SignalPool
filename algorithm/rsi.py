######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
import numpy as np
from tools.indicator import rsi
from tools.updatedata import updatedata
from userchoose.userchoose import Userchoose


class Rsi:
    """
    RSI策略,应用周期：1小时线
    当rsi小于20记录状态为-1，清掉所有多单；
    当rsi大于80记录状态为+1，清掉所有空单；
    状态为-1时，向上突破10根K线高点，做多，止损20低点；
    状态位+1时，向下突破10根K线低点，做空，止损20高点；

    """

    def __int__(self, sid, pid, df, uid=None):
        """

        :param sid: 策略ID
        :param pid: 品种ID
        :param uid: 用户ID
        :param df: 初始化数据表用于后期计算（pandas DataFrame)
        :return:
        """
        self.sid = sid
        self.pid = pid
        self.uid = uid
        self.position = 0
        self.status = 0
        self.stoploss = 0
        self.df = df.iloc[-20 * 60:]

    def algorithm(self, ticker):
        """

        :param ticker: 订阅的数据
        :return:
        """
        price = np.float64(ticker['close'])
        rsi_val = rsi(self.df, n=7 * 60)
        high10 = self.df.iloc[-10 * 60:]['high'].max()
        low10 = self.df.iloc[-10 * 60:]['low'].min()
        high20 = self.df.iloc[-20 * 60:]['high'].max()
        low20 = self.df.iloc[-20 * 60:]['low'].min()
        if rsi_val < 20:
            self.status = -1
            if self.position == 1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)

        elif rsi_val > 80:
            self.status = 1
            if self.position == -1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)
        if self.position == 0:
            if (self.status == -1) and (price > high10):
                self.position = 1
                self.uid = Userchoose().choose(self.pid)
                self.stoploss = low20
            elif (self.status == 1) and (price < low10):
                self.position = -1
                self.uid = Userchoose().choose(self.pid)
                self.stoploss = high20
            else:
                pass
        elif (self.position == 1) and (price < self.stoploss):
            self.position = 0
            self.stoploss = 0
            self.status = 0
            Userchoose().reset(self.uid, self.pid)
        elif (self.position == -1) and (price > self.stoploss):
            self.position = 0
            self.stoploss = 0
            self.status = 0
            Userchoose().reset(self.uid, self.pid)
        else:
            pass
        # 更新分钟k线数据
        self.df = updatedata(self.df, ticker)
