######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np


def getKline(df, interval='day'):
    """
    此函数主要用于Rbreak策略
    由于订阅的数据为分钟数据，因此需要在计算日K、周K时需要换算
    :param df: 输入的分钟数据，类型为pandas DataFrame
    :param interval: 默认为日度K线（也支持周度K线 interval='week'）
    :return: 日度K线(周度K线)open,high,low,close
    """
    if interval == 'week':
        interval = 7 * 24 * 60
    else:
        interval = 24 * 60

    df.sort_values(by='time', inplace=True)
    df = df.iloc[-interval:]
    open_, high, low, close = df.iloc[0]['open'], df.max()['high'], df.min()['low'], df.iloc[-1]['close']
    data = np.array([open_, high, low, close])
    result = pd.DataFrame(data.reshape(1, 4), columns=['open', 'high', 'low', 'close'], dtype=np.float64)
    return result



