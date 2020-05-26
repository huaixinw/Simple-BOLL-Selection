# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 19:15:23 2018

@author: lenovo
"""

import tushare as ts
import pandas as pd
import numpy as np

pro = ts.pro_api()
stock_list = pro.query('stock_basic',
                       exchange='',
                       list_status='L',
                       fields='ts_code,symbol,industry,market,name')

### Boll Index ###
# BOLL_UP: 上轨线位置, 前n天平均+s倍标准差. mean(n)+s*std(n)
# BOLL_DN: 下轨线位置, 前n天平均-s倍标准差. mean(n)-s*std(n)
# BOLL_width: 通道宽度, (上轨线位置-下轨线位置)/均线
# BOLL_%b: (当日收盘价-下轨线位置)/通道宽度

### 搜索策略 ###
# 找到在价格低点的股票: %b<0(或增加条件: 第二天%b>0, 表示存在上升趋势)
# scene1:收盘价低于下轨线
# scene2:柱形图实体在下轨线之上，但前3天内低于下轨

pool_scene1 = list()
pool_scene2 = list()
def BOLL(code,n,s,start,end):
    # 输入: 1.股票代码code;
    #       2.均线天数n
    #       3.标准差倍数s
    #       4.数据开始日期, form: 'yyyymmdd'
    #       5.进行选股的日期, form: 'yyyymmdd'
    # 输出: 将code分类到预先创建的pool中
    
    stock_data = pro.daily(ts_code=code,
                             start_date = start,end_date = end,
                             fields='ts_code,trade_date,open,high,low,close,vol,amount')
    if len(stock_data)>60:
        stock_data = stock_data[::-1]
        stock_data.index = range(0,len(stock_data))
        stock_data['MA'+str(n)] = stock_data['close'].rolling(window=n).mean()
        stock_data['Std'+str(n)] = stock_data['close'].rolling(window=n).std()
        # MA, Std Computation Completed.
        stock_data['BOLL_UP'] = stock_data['MA'+str(n)]+s*stock_data['Std'+str(n)]
        stock_data['BOLL_DN'] = stock_data['MA'+str(n)]-s*stock_data['Std'+str(n)]   
        # %b指标，用来判断交易信号/模式识别
        stock_data['BOLL_%b'] = (stock_data['close']-stock_data['BOLL_DN'])/(stock_data['BOLL_UP']-stock_data['BOLL_DN'])
        # 通道宽度，用来判断趋势
        # 通道缩窄并持续表示即将出现趋势
        stock_data['BOLL_width'] = (stock_data['BOLL_UP']-stock_data['BOLL_DN'])/stock_data['MA'+str(n)]
        # BOLL Index Computation Completed.
        stock_data = stock_data[::-1]
        stock_data.index = range(0,len(stock_data))
        if stock_data['BOLL_%b'][0] < 0:
            pool_scene1.append(code)
        elif min(stock_data['BOLL_%b'][1],stock_data['BOLL_%b'][2],stock_data['BOLL_%b'][3])>0:
            print('judging...')
        else:
            pool_scene2.append(code)
    else:
        # 交易天数过少, drop
        print('few trading days...')
    return print('calculation completed.')

for code in set(stock_list['ts_code']):
    sym = 1
    BOLL(code,20,2,'20180513','20181113')
    sym += 1
    print(sym)

print('Search Complete.')

