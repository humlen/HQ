# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 17:55:15 2023

@author: eirik
"""

import pandas as pd
from tqdm import tqdm
from scipy import stats
import numpy as np
import yfinance as yf
from datetime import date, timedelta

#%%
df_eps = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__eps.csv")
cutoff_date = '2018-01-01'


#%% Does previous linearity predict future linearity?

# Before 2018
tickerlist = df_eps["Ticker"].unique().tolist()
pearson_list = []
    
print("Retrieving Pre-2018 Data...")
for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    df_pearson_eps = df_eps[(df_eps["Ticker"] == ticker)]
    df_pearson_eps = df_pearson_eps[(df_pearson_eps["Date"] <= cutoff_date)]
    df_pearson_eps = df_pearson_eps.reset_index(drop=True)
    try:
        df_pearson_eps = [[ticker, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).statistic, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).pvalue, max(df_pearson_eps.index)+1]]
    except:
        df_pearson_eps = [[ticker,0,0,0]]
         
    df_pearson_eps = pd.DataFrame(df_pearson_eps, columns = ["Ticker", "Pearson R", "Pearson P-Value", "Pearson QNum"])
    pearson_list.append(df_pearson_eps)
 


df_eps_pre19 = pd.concat(pearson_list, axis = 0)   
 
# All Data
tickerlist = df_eps["Ticker"].unique().tolist()
pearson_list = []
    
print("Retrieving Post-2018 Data...")
for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    df_pearson_eps = df_eps[(df_eps["Ticker"] == ticker)]
    df_pearson_eps = df_pearson_eps.reset_index(drop=True)
    try:
        df_pearson_eps = [[ticker, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).statistic, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).pvalue, max(df_pearson_eps.index)+1]]
    except:
        df_pearson_eps = [[ticker,0,0,0]]
         
    df_pearson_eps = pd.DataFrame(df_pearson_eps, columns = ["Ticker", "Pearson R", "Pearson P-Value", "Pearson QNum"])
    pearson_list.append(df_pearson_eps)
 


df_eps_post19 = pd.concat(pearson_list, axis = 0)   

# Join Together 
df_eps_total = df_eps_pre19.merge(df_eps_post19, how = 'left', left_on ="Ticker", right_on = "Ticker", suffixes = ("_Pre","_Post"))
df_eps_total = df_eps_total[(df_eps_total["Pearson QNum_Pre"] >= 10)]
df_eps_total = df_eps_total[(df_eps_total["Pearson QNum_Post"] >= 10)]
df_eps_total = df_eps_total.dropna()
df_eps_total["Pearson R_Pre"] = df_eps_total["Pearson R_Pre"].replace([np.inf,-np.inf],0)
df_eps_total["Pearson R_Post"] = df_eps_total["Pearson R_Post"].replace([np.inf,-np.inf],0)

p_corr = stats.pearsonr(df_eps_total["Pearson R_Pre"],df_eps_total["Pearson R_Post"]).statistic


# Output
print("The Correlation between pre- and -post is: ")
print(p_corr)

if 0 < p_corr < 1:
    print("the correlation is positive")
else:
    print("the correlation is negative")
    
if abs(p_corr) < 0.3:
    print("the correlation is weak")
elif abs(p_corr) < 0.5:
    print("the correlation is moderate")
else:
    print("the correlation is strong")

#%% Is Linearity correlated with returns?

""" This bit is fucked
pricelist = []

# DF of prices for tickers on Cutoff date
for i in tqdm(range(len(tickerlist))):
    try:
        ticker = tickerlist[i]
        hist = yf.download(ticker, start = cutoff_date, end = date.today()-timedelta(days = 1))
        df_prices = pd.DataFrame[ticker,  hist["Close"].iloc[0],hist["Close"].iloc[-1]]
        df = pd.DataFrame(appendlist)
        pricelist.append(df)
    except:
        pass
# DF of prices for tickers today


df_pricelist = pd.concat(pricelist, axis = 0)

#%% Test
# Join

df = pd.DataFrame(columns = ["Ticker","Open","Close"])

for i in tqdm(range(len(tickerlist))):
    try:
        df.append({'Ticker' : df_pricelist[3*i]}, ignore_index = True)
        df.append({'Open' : df_pricelist[3*i+1]}, ignore_index = True)
        df.append({'Ticker' : df_pricelist[3*i+2]}, ignore_index = True)
    except:
        pass

# Output










