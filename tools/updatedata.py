######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime


def updatedata(df, ticker):
    """
    由于订阅的分钟K线在一分钟内推多次，因此更新pandas DataFrame 中的分钟K线数据
    :param df: 需要更新的pandas DataFrame 表
    :param ticker: 订阅的ticker数据
    :return: 更新后的Pandas DataFrame
    """
    ticker['time'] = datetime.fromtimestamp(float(ticker['time'])/1000)
    time = ticker['time']
    tic = pd.DataFrame(dict(ticker), index=[0])
    tic = tic[['open', 'high', 'low', 'close', 'time']]
    if time == df.iloc[-1]['time']:
        df.drop([df.iloc[-1].name], inplace=True)
        df = df.append(tic, ignore_index=True)
        df.index = np.arange(df.shape[0])
    else:
        df = df.append(tic, ignore_index=True)
        df.drop([0], inplace=True)
        df.index = np.arange(df.shape[0])

    df = df.apply(pd.to_numeric(errors='ignore'))
    return df
