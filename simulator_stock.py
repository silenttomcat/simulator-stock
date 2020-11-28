# -*- coding: UTF-8 -*-
import mpl_finance
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import ticker
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
import os
import random
import logging
import re

logging.basicConfig(filename='stock.log',format='[%(asctime)s-:%(message)s]', level = logging.INFO,filemode='a',datefmt='%Y-%m-%d %I:%M:%S %p')

BUYYED = False
buying_price = None
selling_price = None
t_profit = 0.0
profit = 0.0
holding_days = 0

try:
    with open('stock.log') as f:
        history = f.read()
        history_list=history.split("\n")
        t_profit = float(re.search(r'total profit\s+=\s+(.*?)%',history_list[len(history_list)-2]).group(1))/100
except Exception as e:
    profit = 0.0
    print(e)

filename="data\\600006.csv"

def read_csv_and_processing_to_df():
    filename_list=[file for file in os.listdir("data")]
    print(filename_list[:10])
    filename = "data\\"+filename_list[random.randint(1,len(filename_list))]
    print(filename)
    df=pd.read_csv(filename,header=None,encoding="gbk",
        names=["date","code","name","close","high","low","open","fclose","zde","zdf","vol","vol1","mount","allmount","ltmount"],
        skiprows=1,skipfooter=1,usecols=["date","code","close","high","low","open","vol1"],index_col=0,engine="python")
    df=df.sort_values(by=["date"])
    df['dates'] = np.arange(0, len(df))
    df['5'] = df.close.rolling(5).mean()
    df['10'] = df.close.rolling(10).mean()
    df['20'] = df.close.rolling(20).mean()
    df['up'] = df.apply(lambda row: 1 if row['close'] >= row['open'] else 0, axis=1)
    return df

def on_button_press(event):
    print(event.button)
    global df, start , BUYYED , buying_price, selling_price, t_profit , profit, holding_days
    start = start + 1
    if event.button == 1: # left click
        holding_days = holding_days + 1
        if not BUYYED:
            selling_price = None
            BUYYED = True
            buying_price = float(df.iloc[50+start-1]['open'])
            print("buying_price = {} ".format(buying_price))
            #logging.info("buying_price = {} ".format(buying_price))
        else:
            print("buying_price = {} ".format(buying_price))
        profit = ((float(df.iloc[50+start-1]['close'])-buying_price))/buying_price
    if event.button == 2: # mid click
        BUYYED = False
        buying_price = None
        selling_price = None
        #t_profit = 0.0
        profit = 0.0   
        holding_days = 0
        print("reseting ...... ")
        df=read_csv_and_processing_to_df()
        start=random.randint(10,int(len(df)/2))  
        print("len: {} start: {}".format(len(df),start))        
    if event.button == 3: # right click
        if BUYYED:
            BUYYED = False
            selling_price = float(df.iloc[50+start-1]['open'])
            profit = ((selling_price-buying_price))/buying_price
            print("buying_price = {} ".format(buying_price))
            print("selling_price = {} ".format(selling_price))
            print("profit = {:.2f}% ".format(profit*100))
            tmp_profit=(1.0+t_profit)*profit
            print("tmp_profit",tmp_profit)
            t_profit = t_profit + tmp_profit
            logging.info("buying_price = {} selling_price = {} holding_days = {} profit = {:.2f}% ". \
            format(buying_price, selling_price, holding_days, profit*100))
            logging.info("total profit = {:.2f}%".format(t_profit*100))
            holding_days = 0            
            buying_price = None 
            profit = 0.0
            
    plt.cla()
    plt.ion()
    print(df.iloc[50+start-1])
    df1=df.iloc[1+start:50+start]
    draw_stock(df1)
    #plt.pause(1)
    plt.ioff()
    
df=read_csv_and_processing_to_df()
start=random.randint(10,int(len(df)/2))
figure = plt.figure(figsize=(12, 9),facecolor="goldenrod")    
figure.canvas.mpl_connect('button_press_event', on_button_press)

def draw_stock(df):
    global t_profit , buying_price, selling_price, profit
    # select df
    #df=df.iloc[len(df)-50:len(df)]
    #print(df)
    
    #figure = plt.figure(figsize=(12, 9))
    plt.cla()
    
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = 'SimHei'
    
    def format_date(x,pos):
        if x<0 or x>len(date_tickers)-1:
            return ''
        return date_tickers[int(x)]
    
    date_tickers = df.dates.values
    # 
    
    gs = GridSpec(3, 1)
    ax1 = plt.subplot(gs[:2, :],facecolor="black")
    ax2 = plt.subplot(gs[2, :],facecolor="black")
    
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    # 
    mpl_finance.candlestick_ochl(
        ax=ax1,
        quotes=df[['dates', 'open', 'close', 'high', 'low']].values,
        width=0.7,
        colorup='r',
        colordown='cyan',
        alpha=0.7)
    # 
    for ma in ['5', '10', '20']:
        ax1.plot(df['dates'], df[ma])
    #plt.legend()
    ax1.set_title("Total: {:.2f} Profit : {:.2f}% buy price : {}  sell price : {}  temp profit : {:.2f}%".format(20000*(1+t_profit),t_profit*100,buying_price,selling_price,profit*100), fontsize=15)
    
    # 
    ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    #df2['up'] = df.apply(lambda row: 1 if row['close'] >= row['open'] else 0, axis=1)
    ax2.bar(df.query('up == 1')['dates'], df.query('up == 1')['vol1'], color='r', alpha=0.7)
    ax2.bar(df.query('up == 0')['dates'], df.query('up == 0')['vol1'], color='cyan', alpha=0.7)
    ax2.set_xlabel('Stock Simulator', fontsize=30)
    ax2.set_title("Help : mouse left click：buy/keep，  mouse right click：sell/waiting  mouse mid click：reset", fontsize=15)

    
if __name__=="__main__":
    df1=df.iloc[start+1:start+50]
    #print(df1)
    draw_stock(df1)
    plt.show()
