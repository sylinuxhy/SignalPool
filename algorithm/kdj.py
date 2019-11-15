######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
from tools.indicator import kdj
from tools.updatedata import updatedata
from userchoose.userchoose import Userchoose


class Kdj:
    """
    HDJ策略，应用周期：日线+1小时线
    日线kdj金叉情况下，清空所有空单，反手开多，1小时kdj金叉开多，死叉平多
    日线kdj死叉情况下，清空所有多单，反手开空，1小时kdj死叉开空，金叉平空

    """

    def __init__(self, sid, pid, df, uid=None):
        """
        KDJ 策略
        :param sid: 策略ID
        :param pid: 品种ID
        :param uid: 用户ID
        :param df: 初始化数据表用于后期计算（pandas DataFrame)
        """
        self.sid = sid
        self.pid = pid
        self.uid = uid
        self.position = 0
        self.df = df.iloc[-9 * 24 * 60:]

    def algorithm(self, ticker):
        """
        计算部分
        :param ticker: 订阅的数据
        :return:
        """
        df = self.df.iloc[-9 * 60:]
        kdj_dvalue = kdj(self.df, n=9 * 24 * 60, m=3 * 24 * 60)
        kdj_hvalue = kdj(df, n=9 * 60, m=3 * 60)
        d_k, d_d, d_j = kdj_dvalue['kdj_k'], kdj_dvalue['kdj_d'], kdj_dvalue['kdj_j']
        h_k, h_d, h_j = kdj_hvalue['kdj_k'], kdj_hvalue['kdj_d'], kdj_hvalue['kdj_j']
        if (d_k > d_d) and (self.position == -1):
            self.position = 1
        elif (d_k < d_d) and (self.position == 1):
            self.position = -1
        elif h_k > h_d:
            if self.position == 0:
                self.position = 1
                self.uid = Userchoose().choose(self.pid)
            elif self.position == -1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)
        elif h_k < h_d:
            if self.position == 0:
                self.position = -1
                self.uid = Userchoose().choose(self.pid)
            elif self.position == 1:
                self.position = 0
                Userchoose().reset(self.uid, self.pid)

        self.df = updatedata(self.df, ticker)
