# -*- coding: utf-8 -*-  
import pandas as pd
import numpy as np
import talib as ta
from matplotlib import pyplot as plt 
import matplotlib
import datetime
import pymongo
import requests
import json
from QMODEL import qma01
import sys

token0 = sys.argv[1]
token1 = sys.argv[2]
tokens = token0+token1
period = sys.argv[3]
dbtype = sys.argv[4]


# 读取火币K线数据
HuoBiAPI= "https://api.huobi.pro/market/history/kline?period="+period+"&size=2000&symbol="+tokens
# HuoBiAPI= "https://api.huobi.pro/market/history/kline?period=60min&size=2000&symbol=bchusdt"
# HuoBiAPI= "https://api.huobi.pro/market/history/kline?period=60min&size=2000&symbol=eosusdt"
# HuoBiAPI= "https://api.huobi.pro/market/history/kline?period=60min&size=2000&symbol=ethusdt"

r=requests.get(HuoBiAPI)
if r.status_code != 200:
    print("httpGet failed,detail is:%s,%s" %(response.text))
    exit()
print("httpGet OK!")
data = r.json()
djson = json.dumps(data['data'])

# 列对齐
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

# 导入数据
df = pd.read_json(djson,orient='records')


# 时间格式转换
for index in df.index:
    timeStamp = df.loc[index,'id']
    # timeStamp = int(timeStamp/1000)
    dateArray = datetime.datetime.fromtimestamp(timeStamp)
    df.loc[index,'datetime'] = dateArray.strftime("%Y-%m-%d %H:%M:%S")
# df['datetime'] = pd.to_datetime(df['id'],utc=True, unit='s')

# df['datetime'] = df['id']

# print(df.head())
df2 = df[['datetime','open','close','low','high','amount','count','vol']]

# 排序
df2 = df2.sort_values(by = 'datetime',ascending=True)
df2 = df2.reset_index(drop=True)

close = np.array(df2['close'].values,dtype='f8')
# 获取MACD macd(对应diff),macdsignal(对应dea),macdhist(对应macd)
df2['DIFF'], df2['DEA'], df2['MACD']  = ta.MACD(close,  fastperiod=12, slowperiod=26, signalperiod=9) 
# 获取均线
df2['MA5'] = ta.MA(close, timeperiod=5)
df2['MA10'] = ta.MA(close, timeperiod=10)
df2['MA20'] = ta.MA(close, timeperiod=20)
df2['MA60'] = ta.MA(close, timeperiod=60)

if dbtype == 'csv'
    bakfilename = "HuoBi_"+tokens+"_"+period.csv"
    df2.to_csv(bakfilename,index=False)
    print("Data backup to ->"+bakfilename)

if dbtype == 'mongodb'
    myclient = pymongo.MongoClient("mongodb://47.94.96.48:27017/")
    mydb = myclient["huobi"]
    mycol = mydb[tokens+period]
    try:
        mycol.remove({})
        print("MongdoDB removing!!!")
    mycol.insert_many(json.loads(df2.T.to_json()).values())
    print("INPUT MongoDB OK!")

# 执行交易策略
# qma01.dttest(df2)
# print('='*60)
