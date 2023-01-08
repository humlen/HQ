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
from datetime import datetime, timedelta

# Only enable if you know what you're doing
import warnings 
warnings.filterwarnings("ignore")


#%% Preparations

# Needs to be fixed: read from CSV
tickerlist = ['msft','aapl','goog']
companylist = ['microsoft','apple','alphabet']
start_date = '1993-09-25'
end_date = datetime.now()+timedelta(days=-730)
list_roa = []
list_prices = []
mt =  "https://www.macrotrends.net/stocks/charts/"

print(end_date)

#%% YFinance Equity Price Collection
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
  df_price = df_price[(df_price['Date'] >= start_date)]
  df_dates = pd.DataFrame({'Date':pd.date_range(start=start_date, end=datetime.today())})
  df_price = pd.merge(df_dates, df_price, how = 'left', left_on='Date', right_on = 'Date')
  df_price = df_price.ffill(axis=0)
#  DF= pd.merge(df_roa, df_prices, how='left', left_on=['Date','Ticker'], right_on=['Date','Ticker']) # 93/135 test data joined (68.9%)

  # Append to list of dataframes
  list_prices.append(df_price)
  
df_prices = pd.concat(list_prices, axis = 0) 

# Create list of dates from 1993-01-01 until today
#df_dates = pd.DataFrame({'Date':pd.date_range(start='1993-09-25', end=datetime.today())})



#%% YFinance Target Index Price Collection'
print(df_prices.head(25))

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
  Q_Roa['Date'] = Q_Roa['Date'].astype('datetime64')
  Q_Roa = Q_Roa[(Q_Roa['Date'] >= start_date) & (Q_Roa['Date']< end_date)]

  # Append to list of dataframes
  
  list_roa.append(Q_Roa)

# Concatenate dataframes
df_roa = pd.concat(list_roa, axis = 0)

#%% Combine Price & ROA Data

df_base = pd.merge(df_roa, df_prices, how='left', left_on=['Date','Ticker'], right_on=['Date','Ticker']) 
df_base["6 Months"] = df_base["Date"] + timedelta(days=182)
df_base["1 Year"] = df_base["Date"]+ timedelta(days=365)
df_base["2 Years"] = df_base["Date"]+timedelta(days=730)
df_base = df_base.drop(['Net Income','Assets'], axis = 1)
df_base = pd.merge(df_base, df_prices, how='left', left_on=['6 Months','Ticker'], right_on=['Date','Ticker'], suffixes=('','_6m')) 
df_base = pd.merge(df_base, df_prices, how='left', left_on=['1 Year','Ticker'], right_on=['Date','Ticker'], suffixes= ('','_1y')) 
df_base = pd.merge(df_base, df_prices, how='left', left_on=['2 Years','Ticker'], right_on=['Date','Ticker'], suffixes= ('','_2y'))
df_base = df_base.drop(['Date_6m','Date_1y','Date_2y'], axis = 1)

#%% Calculate returns per ROA
df_base.info()
print(df_base.tail(10))


