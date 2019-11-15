######################################################################
# Created by Zu Bing Fang @58coin, all rights reserved to 58Coin     #
#                                                   Nov,14,2019      #
######################################################################

# -*- coding:utf-8 -*-
import pandas as pd


def macd(data, short=12, long=26, mid=9):
    """
    计算MACD指标
    :param data: 输入的数据
    :param short: 短周期
    :param long: 长周期
    :param mid: 中周期
    :return:
    """
    data['sema'] = data['close'].ewm(span=short).mean()
    data['lema'] = data['close'].ewm(span=long).mean()
    data.fillna(0, inplace=True)
    data['diff'] = data['sema'] - data['lema']
    data['dea'] = data['diff'].ewm(span=mid).mean()
    data['macd'] = 2 * data['diff'] - data['dea']
    data.fillna(0, inplace=True)
    return data[['diff', 'dea', 'macd']].iloc[-1]


def kdj(data, n=9, m=3):
    """
    计算KDJ指标
    :param data: 输入的数据
    :param n: 长周期
    :param m: 短周期
    :return:
    """
    low = data['low'].rolling(n).mean()
    low.fillna(value=data['low'].expanding().min(), inplace=True)
    high = data['high'].rolling(n).max()
    high.fillna(value=data['high'].expanding().max(), inplace=True)
    rsv = (data['close'] - low) / (high - low) * 100
    data['kdj_k'] = rsv.ewm(com=m).mean()
    data['kdj_d'] = data['kdj_k'].ewm(com=m).mean()
    data['kdj_j'] = 3 * data['kdj_k'] - 2 * data['kdj_d']
    data.fillna(0, inplace=True)
    return data[['kdj_k', 'kdj_d', 'kdj_j']].iloc[-1]


def ma(data, n=5):
    """
    计算MA指标
    :param data: 输入的数据
    :param n: 计算周期
    :return:
    """
    data['ma'] = data['close'].rolling(n).mean()
    data.fillna(0, inplace=True)
    return data[['ma']]


def std(data, n=5):
    """
    计算移动标准差
    :param data:输入的数据
    :param n: 计算周期
    :return:
    """
    data['std'] = data['close'].rolling(n).std()
    data.fillna(0, inplace=True)
    return data[['std']].iloc[-1]


def rsi(data, n=24):
    """
    计算RSI指标
    :param data: 输入的数据
    :param n: 计算周期
    :return:
    """
    data['value'] = data['close'] - data['close'].shift(1)
    data.fillna(0, inplace=True)
    data['value1'] = data['value']
    data['value1'][data['value1'] < 0] = 0
    data['value2'] = data['value']
    data['value2'][data['value2'] > 0] = 0
    data['plus'] = data['value1'].rolling(n).sum()
    data['minus'] = data['value2'].rolling(n).sum()
    data.fillna(0, inplace=True)
    data['rsi'] = data['plus'] / (data['plus'] - data['minus']) * 100
    data.fillna(0, inplace=True)
    return data[['rsi']].iloc[-1]


def cci(data, n=14):
    """
    计算CCI指标
    :param data: 输入的数据
    :param n: 计算周期
    :return:
    """
    data['tp'] = (data['high'] + data['low'] + data['close']) / 3
    data['mac'] = data['tp'].rolling(n).mean()
    data['mac'] = data['close'].rolling(n).mean()
    data['md1'] = data['mac'] - data['close']
    data.fillna(0, inplace=True)
    data['md'] = data['md1'].rolling(n).mean()
    data['cci'] = (data['tp'] - data['mac']) / (data['md'] * 0.015)
    return data[['cci']].iloc[-1]
