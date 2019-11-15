######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-

import numpy as np
from datetime import datetime
from tools.getKline import getKline
from tools.updatedata import updatedata
from userchoose.userchoose import Userchoose


class Rbreakday:
    """
    Created by Zubing Fang, Zichen Liu
    All Rights reserved to 58coin

    Rbreak 日度周期策略
    以前一日的日内最高价、最低价、收盘价计算 观察卖出价、观察买入价、反转卖出价、反转买入价、突破买入价、突破卖出价等6个指标

    1）反转开仓策略:
    持有多单情况下，当日内最高价超过观察卖出价（参数）后，盘中价格出现回落，且进一步跌破反转卖出价（参数）构成的支撑线时，采取反转策略，即在该点位反手做空；
    持有空单情况下，当日内最低价低于观察买入价（参数）后，盘中价格出现反弹，且进一步超过反转买入价（参数）构成的阻力线时，采取反转策略，即在该点位反手做多；
    空仓情况下，当日内最高价超过观察卖出价（参数）后，盘中价格出现回落，且进一步跌破反转卖出价（参数）构成的支撑线时，采取反转策略，即在该点位做空，止损位置为突破买入价（参数）；
    空仓情况下，当日内最低价低于观察买入价（参数）后，盘中价格出现反弹，且进一步超过反转买入价（参数）构成的阻力线时，采取反转策略，即在该点位做多，止损位置为突破卖出价（参数）；

    2）突破开仓策略:
    在空仓的情况下，如果盘中价格超过突破买入价（参数），则采取趋势策略，即在该点位开仓做多，止损位置为反转买入价（参数）；
    在空仓的情况下，如果盘中价格跌破突破卖出价（参数），则采取趋势策略，即在该点位开仓做空，止损位置为反转卖出价（参数）；

    3）平仓策略：
    收盘前5分钟平仓

    4）关键价位计算方式：
    观察卖出价 = High + 0.35 * (Close – Low)
    观察买入价 = Low – 0.35 * (High – Close)
    反转卖出价 = 1.07 / 2 * (High + Low) – 0.07 * Low
    反转买入价 = 1.07 / 2 * (High + Low) – 0.07 * High
    突破买入价 = 观察卖出价 + 0.25 * (观察卖出价 – 观察买入价)
    突破卖出价 = 观察买入价 – 0.25 * (观察卖出价 – 观察买入价)
    """

    def __init__(self, sid, pid, df, uid=None, obs=0.35, rev=0.07, bre=0.25):
        """
        :param sid: 策略ID
        :param pid: 品种ID
        :param uid: 用户ID
        :param df : 输入的初始化数据
        :param obs: 观察价参数
        :param rev: 反转价参数
        :param bre: 突破价参数
        """
        self.sid = sid
        self.pid = pid
        self.uid = uid
        self.df = df.iloc[-24 * 60:]
        self.obs = obs
        self.rev = rev
        self.bre = bre
        self.position = 0
        self.stopLoss = 0
        self.rBreak = 0
        self.upperObserveSell = 0
        self.lowerObserveBuy = 0
        self.upperReverseBuy = 0
        self.lowerReverseSell = 0
        self.opentime = 0
        data = getKline(self.df)
        a, b, c, d, e, f = self.get_mark(data)
        self.observeSellprice = a
        self.observeBuyprice = b
        self.reverseSellprice = c
        self.reverseBuyprice = d
        self.breakBuyprice = e
        self.breakSellprice = f

    def get_mark(self, data=None):
        """
        计算次日参数
        :param data: 从数据库提取的前一日高、低、开、收价
        :return:
        """
        if data is None:
            return 0, 0, 0, 0, 0, 0

        oSp = data.high + self.obs * (data.close - data.low)
        oBp = data.low - self.obs * (data.high - data.close)
        rSp = (1. + self.rev) / 2 * (data.high + data.low) - self.rev * data.low
        rBp = (1. + self.rev) / 2 * (data.high + data.low) - self.rev * data.high
        bBp = oSp + self.bre * (oSp - oBp)
        bSp = oBp + self.bre * (oSp - oBp)

        return oSp.values, oBp.values, rSp.values, rBp.values, bBp.values, bSp.values

    def algorithm(self, ticker):
        """

        :param ticker: socket 收到的ticker数据，用pandas包装
        :return:
        """
        date = datetime.now()
        price = np.float64(ticker['close'])
        if self.position == 0:

            if price > self.breakBuyprice:
                self.position = 1
                self.rBreak = 1
                self.stopLoss = self.reverseBuyprice
                self.uid = Userchoose().choose(self.pid)

            elif price < self.breakSellprice:
                self.position = -1
                self.rBreak = -1
                self.stopLoss = self.reverseSellprice
                self.opentime = date
                self.uid = Userchoose().choose(self.pid)
                content = "空仓的情况下，盘中价格在{}跌破突破卖出价 {}，采取趋势策略，在该点位开仓做空，止损位置为反转" \
                          "卖出价 {}".format(str_date, self.breakSellprice, self.reverseSellprice)

            elif (price > self.observeBuyprice) and (price < self.breakBuyprice):
                self.upperObserveSell = 1

            elif (price < self.observeSellprice) and (price < self.breakSellprice):
                self.lowerObserveBuy = 1

            elif (self.upperObserveSell == 1) and (price < self.breakSellprice):
                self.position = -1
                self.stopLoss = self.breakBuyprice
                self.opentime = date
                self.uid = Userchoose().choose(self.pid)
                content = "空仓情况下，日内最高价超过观察卖出价{}后，盘中价格出现回落，且在{}进一步跌破反转卖出价{}" \
                          "构成的支撑线时，采取反转策略，即在该点位做空，止损位置为突破买入价{}".format(self.observeSellprice, str_date,
                                                                       self.reverseSellprice, self.breakBuyprice)

            elif (self.lowerObserveBuy == 1) and (price > self.reverseBuyprice):
                self.position = 1
                self.stopLoss = self.breakSellprice
                self.opentime = date
                self.uid = Userchoose().choose(self.pid)
                content = "空仓情况下，当日内最高价低于观察买入价{}后，盘中价格出现反弹，且进一步在{}超过反转买入价{}" \
                          "构成的阻力线时，采取反转策略，即在该点位做多，止损位置为突破卖出价{}".format(self.observeBuyprice, str_date,
                                                                       self.reverseBuyprice, self.breakSellprice)

            else:
                pass

        else:

            if (self.position == 1) and (self.rBreak != 1):

                if price > self.observeSellprice:
                    self.upperObserveSell = 1

                elif (self.upperObserveSell == 1) and (price < self.reverseSellprice):
                    self.position = -1
                    self.stopLoss = self.breakBuyprice
                    self.opentime = date
                    content = "持有多单情况下，当日内最高价超过观察卖出价{}后，盘中价格出现回落，且进一步在{}跌破反转卖" \
                              "出价{}构成的支撑线时，采取反转策略，即在该点位反手做空," \
                              "止损位置为突破买入价{}".format(self.observeSellprice, str_date, self.reverseSellprice,
                                                    self.breakBuyprice)

                else:
                    pass

            elif (self.position == -1) and (self.rBreak != -1):

                if price < self.observeBuyprice:
                    self.lowerObserveBuy = 1

                elif (self.lowerObserveBuy == 1) and (price > self.reverseBuyprice):
                    self.position = 1
                    self.stopLoss = self.breakSellprice
                    self.opentime = date
                    content = "持有空单情况下，当日内最低价低于观察买入价{}后，盘中价格出现反弹，且进一步在{}超过反转买" \
                              "入价{}构成的阻力线时，采取反转策略，即在该点位反手做多，" \
                              "止损位置为突破卖出价{}".format(self.observeBuyprice, str_date, self.reverseBuyprice,
                                                    self.breakSellprice)

                else:
                    pass

            elif (date >= datetime(year=self.opentime.year, month=self.opentime.month, day=self.opentime.day, hour=23,
                                   minute=55, second=0)) and self.position:
                str_time = date.strftime('%Y-%m-%d %H:%M')
                self.stopLoss = 0
                if self.position == 1:
                    self.opentime = 0
                    self.position = 0
                    Userchoose().reset(self.uid, self.pid)
                    if self.rBreak == 1:
                        self.rBreak = 0
                        content = "持有的{}价位的多单，以收盘前5分钟时间{} ({})的价格{}平仓".format(str_date, self.breakBuyprice, str_time,
                                                                              price)

                    else:
                        content = "持有的{}价位的多单，以收盘前5分钟时间{} ({})的价格{}平仓".format(str_date, self.reverseBuyprice, str_time,
                                                                              price)

                else:
                    self.position = 0
                    self.opentime = 0
                    Userchoose().reset(self.uid, self.pid)
                    if self.rBreak == -1:
                        self.rBreak = 0
                        content = "持有以{}价位的空单，以收盘前5分钟时间{} ({})的价格{}平仓".format(str_date, self.breakSellprice, str_time,
                                                                              price)

                    else:
                        content = "持有以{}价位的空单，以收盘前5分钟时间{} ({})的价格{}平仓".format(str_date, self.reverseSellprice, str_time,
                                                                              price)

            else:

                if (self.position == 1) and (price < self.stopLoss):
                    self.position = 0
                    self.opentime = 0
                    stoploss = self.stopLoss
                    self.stopLoss = 0
                    Userchoose().reset(self.uid, self.pid)
                    if self.rBreak == 1:
                        self.rBreak = 0
                        content = "持有以{}价位的多单，目前在{}价格跌破止损价位{},以市价单止损平仓".format(str_date, self.breakBuyprice, stoploss)

                    else:
                        content = "持有以{}价位的多单，目前在{}价格跌破止损价位{},以市价单止损平仓".format(str_date, self.reverseBuyprice, stoploss)

                elif (self.position == -1) and (price > self.stopLoss):
                    self.position = 0
                    self.opentime = 0
                    stoploss = self.stopLoss
                    self.stopLoss = 0
                    Userchoose().reset(self.uid, self.pid)
                    if self.rBreak == -1:
                        self.rBreak = 0
                        content = "持有以{}价位的空单，目前在{}价格突破止损价位{},以市价单止损平仓".format(str_date, self.breakSellprice, stoploss)

                    else:
                        content = "持有以{}价位的空单，目前在{}价格突破止损价位{},以市价单止损平仓".format(str_date, self.reverseSellprice,
                                                                               stoploss)

                else:
                    pass

        self.df = updatedata(self.df, ticker)
