# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-06

This research document aims to investigate the impact ROA / ROE / ROI / ROIC 
have on future performances of stocks.
"""

#%% Package Installs
import pandas as pd
import yfinance as yf
from datetime import timedelta

# Only enable if you know what you're doing
import warnings 
warnings.filterwarnings("ignore")


#%% Preparations

# Needs to be fixed: read from CSV
tickerlist = ['msft','aapl','goog']
companylist = ['microsoft','apple','alphabet']
list_roa = []
list_prices = []
mt =  "https://www.macrotrends.net/stocks/charts/"


#%% YFinance Price Collection
# Loop through elements in 
for i in range(len(tickerlist)):
  # Collect Ticker
  ticker = tickerlist[i]
  stock_data = yf.Ticker(ticker)
  stock_hist = stock_data.history(period="max")
  df_price = stock_hist[["Close"]]
  df_price["Ticker"] = ticker
  df_price.reset_index(inplace=True)
  df_price.columns= ['Date','Close','Ticker']
  
  # Append to list of dataframes
  list_prices.append(df_price)
  
df_prices = pd.concat(list_prices, axis = 0) 

#%% ROA Calculation

# Loop through list elements to collect data
for i in range(len(tickerlist)):
  # Collect Ticker
  ticker = tickerlist[i]
  # Collect Company Name
  company = companylist[i]
  # Get ROA-table from Macrotrends
  roa = "{base}{ticker}/{company}/roa".format(ticker=ticker,company=company,base=mt)
  # Remake into a dataframe
  Q_Roa = pd.read_html(roa)[0]
  Q_Roa["Ticker"] = ticker
  Q_Roa.columns= ['Date','Net Income','Assets','ROA','Ticker']

  # Append to list of dataframes
  
  list_roa.append(Q_Roa)

# Concatenate dataframes
df_roa = pd.concat(list_roa, axis = 0)
df_roa['Date'] = df_roa['Date'].astype('datetime64')

#%% Combine Price & ROA Data

df_roa.info()
df_prices.info()

print(df_prices.tail())

#%%
df_base = pd.merge(df_roa, df_prices, how='left', left_on=['Date','Ticker'], right_on=['Date','Ticker']) # 114/156 test data joined (73%)
df_base.info()