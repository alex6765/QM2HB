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
from QMODEL import qma01,TokenCost
from huobiAPI.HuobiServices import *

# 读取火币K线数据
HuoBiAPI= "https://api.huobi.pro/market/history/kline?period=60min&size=200&symbol=eosusdt"
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
df2['macd'], df2['macdsignal'], df2['macdhist']  = ta.MACD(close,  fastperiod=12, slowperiod=26, signalperiod=9) 
# 获取均线
df2['MA5'] = ta.MA(close, timeperiod=5)
df2['MA10'] = ta.MA(close, timeperiod=10)
df2['MA20'] = ta.MA(close, timeperiod=20)
df2['MA60'] = ta.MA(close, timeperiod=60)

#保存CSV
bakfilename = "HUOBI_BTCUSDT_"+df2['datetime'].head(1).values[0]+'_'+df2['datetime'].tail(1).values[0]+".csv"
df2.to_csv(bakfilename,index=False)
print("Data backup to ->"+bakfilename)

# 导入mongodb
# myclient = pymongo.MongoClient("mongodb://47.94.96.48:27017/")
# mydb = myclient["huobi"]
# mycol = mydb["eosusdt60min"]
# mycol.insert_many(json.loads(df2.T.to_json()).values())

# print("INPUT MongoDB OK!")

# 执行交易策略
signal = qma01.dttest(df2)
# signal = 'P'
token0 = 'eos'
token1 = 'usdt'
tokens = token0+token1
cost = TokenCost.mycost(tokens)
print('%s Cost: %s'%(tokens,cost))
print('='*10)
def tbalance(cu='usdt'):
    while True:
        try:
            accinfo = get_balance()
            break
        except:
            print('GET BALANCE ERROR!')

    blist = accinfo['data']['list']
    cubalance = 0
    for i in range(len(blist)):
        if blist[i]['currency'] == cu and blist[i]['type']=='trade':
            cubalance = float(blist[i]['balance'])
    return cubalance
    
if signal == 'B':
    tbalance = tbalance()
    tt = len(df.index)-1
    close = df2.loc[tt,'close'] 
    print(token0+'_close:'+str(close))
    if tbalance >0:
        if tbalance >=5:
            buynum = int(5/close*10000)/10000
        else:
            buynum = int(tbalance/close*10000)/10000
        print('%s balance:%s ,buy%s: %s'%(token1,tbalance,token0,buynum))
        buyrep = send_order(buynum, 'api', tokens, 'buy-market')
        print(buyrep)
    else:
        print('%s balance:%s <=0'%(token1,tbalance))
elif signal == 'S':
    tt = len(df.index)-1
    close = df2.loc[tt,'close'] 
    print(token0+'_close:'+str(close))
    tbalance = tbalance(token0)

    # tbalance = 0.0001
    if tbalance > 0 and close > cost:
        sellnum = int(tbalance*10000)/10000
        if sellnum >0:
            sellrep = send_order(sellnum, 'api', tokens, 'sell-market')
            print(sellrep)
        print('%s balance:%s ,sellnum: %s'%(token0,tbalance,sellnum))
    else:
        print('%s balance:%s <=0'%(token0,tbalance))
else:
    print(signal)
print('='*10)
print('%s Cost: %s'%(tokens,cost))
print('='*10)
print('='*10)



