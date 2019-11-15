######################################################################
# Created by ZuBing Fang @58coin, all rights reserved to 58Coin      #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
import numpy as np
from tools.indicator import cci
from tools.updatedata import updatedata
from userchoose.userchoose import Userchoose


class Cci:
    """
    CCI 策略，应用周期：30分钟线
    当cci小于-100记录状态为-1，清掉所有空单；
    当cci大于100记录状态为+1，清掉所有多单；
    状态为-1时，向上突破10根K线高点，做多，止损10低点；
    状态位+1时，向下突破10根K线低点，做空，止损10高点；

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
        self.df = df.iloc[-10 * 30:]
        self.position = 0
        self.status = 0
        self.stoploss = 0

    def algorithm(self, ticker):
        """

        :param ticker: 订阅的数据
        :return:
        """
        price = np.float64(ticker['close'])
        high10 = self.df.iloc[-10 * 30:]['high'].max()
        low10 = self.df.iloc[-10 * 30:]['low'].min()
        cci_val = cci(self.df, n=14 * 30)
        if cci_val < -100:
            self.status = -1
            if self.position == -1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)
        elif cci_val > 100:
            self.status = 1
            if self.position == 1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)
        if self.position == 0:
            if (self.status == -1) and (price > high10):
                self.position = 1
                self.stoploss = low10
                self.uid = Userchoose().choose(self.pid)
            elif (self.status == 1) and (price < low10):
                self.postion = -1
                self.stoploss = high10
                self.uid = Userchoose().choose(self.pid)
        elif (self.position == 1) and (price < self.stoploss):
            self.position = 0
            Userchoose().reset(self.uid, self.pid)
        elif (self.position == -1) and (price > self.stoploss):
            self.postion = 0
            Userchoose().reset(self.uid, self.pid)
        else:
            pass
        # 更新分钟K线数据
        self.df = updatedata(self.df, ticker)
