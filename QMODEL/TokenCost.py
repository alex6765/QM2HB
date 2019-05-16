#!/usr/bin/env python
# coding: utf-8
from huobiAPI.HuobiServices import *
import pandas as pd
import pymongo
import json

def mycost(token):
    orders = orders_list(token,'filled')
    
    # 更新数据库
    if orders['data']:
        print('DATA = NONE')
    else:
        df = pd.DataFrame.from_dict(orders['data'])
        print(df)
        myclient = pymongo.MongoClient("mongodb://47.94.96.48:27017/")
        mydb = myclient["huobi"]
        mycol = mydb['orders'+token]
        mycol.remove({})
        mycol.insert_many(json.loads(df.T.to_json()).values())
        print(" %s Orders Input MongoDB OK!" %token)

    buylist = ['buy-market','buy-limit']
    sellist = ['sell-market','sell-limit']
    cash = 0.0
    tokens = 0.0
    for i in df.index:
        if df.loc[i,'type'] in buylist:
            cash += float(df.loc[i,'field-cash-amount'])
            tokens += float(df.loc[i,'field-amount'])
        elif df.loc[i,'type'] in sellist:
            cash -= float(df.loc[i,'field-cash-amount'])
            tokens -= float(df.loc[i,'field-amount'])

    cost= cash/tokens*1.002
    # print('GET ORDERS: %s'%orders)
    # print('MY COST:%s'%cost)
    return cost



# df.to_excel('orders.xlsx')