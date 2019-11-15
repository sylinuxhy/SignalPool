######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
from tools.indicator import macd
from tools.updatedata import updatedata
from userchoose.userchoose import Userchoose


class Macd:
    """
    MACD 策略,应用周期日线+1小时线
    日线macd金叉情况下，清空所有空单，反手开多，1小时macd金叉开多，死叉平多
    日线macd死叉情况下，清空所有多单，反手开空，1小时macd死叉开空，金叉平空

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
        self.df = df.iloc[-26 * 24 * 60:]
        self.position = 0

    def algorithm(self, ticker):
        df = self.df.iloc[-26 * 60:]
        macd_dval = macd(self.df, short=12 * 24 * 60, long=26 * 24 * 60, mid=9 * 24 * 60)
        macd_hval = macd(df, short=12 * 60, long=26 * 60, mid=9 * 60)
        d_diff = macd_dval['diff']
        d_dea = macd_dval['dea']
        h_diff = macd_hval['diff']
        h_dea = macd_hval['dea']
        if (d_diff > d_dea) and (self.position == -1):
            self.position = 1
        elif (d_diff < d_dea) and (self.position == 1):
            self.position = -1
        elif h_diff > h_dea:
            if self.position == 0:
                self.position = 1
                self.uid = Userchoose().choose(self.pid)
            elif self.position == -1:
                self.position = 0
                self.uid = Userchoose().choose(self.pid)
        elif h_diff < h_dea:
            if self.position == 0:
                self.position = -1
                Userchoose().reset(self.uid, self.pid)
            elif self.position == 1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)

        self.df = updatedata(self.df, ticker)
