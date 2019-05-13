# model 定投模型
# -*- coding: utf-8 -*-  
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt 
import datetime
import requests


def dttest(df):

    # 获取服务器时间
    ServerTimeAPI="https://api.huobi.pro/v1/common/timestamp"
    res=requests.get(ServerTimeAPI)
    ST=res.json()
    timeStamp = ST['data']
    timeStamp = int(timeStamp/1000)
    dateArray = datetime.datetime.fromtimestamp(timeStamp)
    dttime = dateArray.strftime("%Y-%m-%d %H:%M:%S")

    tt = len(df.index)-2
    # print(df.tail(2))
    print(df.iloc[[tt]])
#    if True:
    if df.loc[tt,'close'] < df.loc[tt,'MA5'] < df.loc[tt,'MA10'] < df.loc[tt,'MA20'] < df.loc[tt,'MA60']:
        print('BuyTime:'+dttime+':close:%s , <MA5:%s, <MA10:%s, <MA20:%s, <MA60:%s' %(df.loc[tt,'close'],df.loc[tt,'MA5'],df.loc[tt,'MA10'],df.loc[tt,'MA20'],df.loc[tt,'MA60']))
        return('B')
    elif df.loc[tt,'close'] > df.loc[tt,'MA5'] > df.loc[tt,'MA10'] > df.loc[tt,'MA20'] > df.loc[tt,'MA60']:
        print('SellTime:'+dttime+':close:%s , >MA5:%s, >MA10:%s, >MA20:%s, >MA60:%s' %(df.loc[tt,'close'],df.loc[tt,'MA5'],df.loc[tt,'MA10'],df.loc[tt,'MA20'],df.loc[tt,'MA60']))
        return('S')
    else:
        print('PASS THIS TIME!')
        return('P')

