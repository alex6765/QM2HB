#!/usr/bin/env python
# coding: utf-8
from huobiAPI.HuobiServices import *
import pandas as pd
import json

def mycost(token):
    orders = orders_list(token,'filled')
    df = pd.DataFrame.from_dict(orders['data'])
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