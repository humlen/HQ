# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 14:20:51 2023

@author: eirik
"""

#%% Package Installs
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import seaborn as sns
import time
import random
from tqdm import tqdm


# SNS
sns.set_style("white")


# Only enable if you know what you're doing
import warnings 
warnings.filterwarnings("ignore")


#%% Preparations

df_tickers = pd.read_csv("Research Resources/Tickers.csv") #1036 Entries
df_tickers = df_tickers.drop_duplicates(subset=["comp_name"])
start_date = '2010-01-01'
end_date = datetime.now()+timedelta(days=-730)
list_roi = []
list_prices = []
mt =  "https://www.macrotrends.net/stocks/charts/"
country_code = "United States"


"""
4365 Companies in Tickerdata
"""

# US Stocks Only
df_tickers = df_tickers[(df_tickers['country_code'] == country_code)]
# 3367 Stocks Left

# Remove Microcaps (Below 100M )
df_tickers = df_tickers[(df_tickers['market_val'] >= 100)]
# 2594 Left

tickerlist = df_tickers["ticker"].to_list()
companylist = df_tickers["comp_name"].to_list()


#%% YFinance Equity Price Collection

# Loop through elements in 
for i in tqdm(range(len(tickerlist))):
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
  sleeptime = random.randint(0,2)
  # Append to list of dataframes
  list_prices.append(df_price)
  
  # Naptime
 # time.sleep(sleeptime)
  
  
  
df_prices = pd.concat(list_prices, axis = 0) 
df_prices = df_prices.dropna()

#%% ROI Data Collection

# Loop through list elements to collect data
print("Be patient, this will take some time...")
for i in tqdm(range(len(tickerlist))):
  # Collect Ticker
  ticker = tickerlist[i]
  # Collect Company Name
  company = companylist[i]
  # Get ROI-table from Macrotrends
  roi = "{base}{ticker}/{company}/roi".format(ticker=ticker,company=company,base=mt)
  # Remake into a dataframe
  try:
      df_roi = pd.read_html(roi)[0]
      df_roi["Ticker"] = ticker
      df_roi.columns= ['Date','Net Income','Assets','ROI','Ticker']
      df_roi['Date'] = df_roi['Date'].astype('datetime64')
      df_roi = df_roi[(df_roi['Date'] >= start_date) & (df_roi['Date']< end_date)]
      list_roi.append(df_roi)
      # Naptime
      sleeptime = random.randint(0,10)
      time.sleep(sleeptime)
  except:
      pass



  # Append to list of dataframes
  

# Concatenate dataframes
df_roi = pd.concat(list_roi, axis = 0)


#%% YFinance Target Index Price Collection

spy_data = yf.Ticker("SPY")
spy_hist = spy_data.history(period="max")
df_spy = spy_hist[["Close"]]
df_spy["Ticker"] = '"SPY"'
df_spy.reset_index(inplace=True)
df_spy.columns= ['Date','SPY','Ticker']
df_spy = df_spy[(df_spy['Date'] >= start_date)]
df_spy = pd.merge(df_dates, df_spy, how = 'left', left_on='Date', right_on = 'Date')
df_spy = df_spy.ffill(axis=0)

#%% Combine Price & ROA Data

df_base = pd.merge(df_roi, df_prices, how='left', left_on=['Date','Ticker'], right_on=['Date','Ticker']) 
df_base["6 Months"] = df_base["Date"] + timedelta(days=182)
df_base["1 Year"] = df_base["Date"]+ timedelta(days=365)
df_base["2 Years"] = df_base["Date"]+timedelta(days=730)
df_base = df_base.drop(['Net Income','Assets'], axis = 1)
df_base = pd.merge(df_base, df_prices, how='left', left_on=['6 Months','Ticker'], right_on=['Date','Ticker'], suffixes=('','_6m')) 
df_base = pd.merge(df_base, df_prices, how='left', left_on=['1 Year','Ticker'], right_on=['Date','Ticker'], suffixes= ('','_1y')) 
df_base = pd.merge(df_base, df_prices, how='left', left_on=['2 Years','Ticker'], right_on=['Date','Ticker'], suffixes= ('','_2y'))
#df_base = df_base.drop(['Date_6m','Date_1y','Date_2y'], axis = 1)

#%% Widen Table

# Add SPY
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date', right_on = 'Date', suffixes = ('','_2'))
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date_6m', right_on = 'Date', suffixes = ('','_6m'))
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date_1y', right_on = 'Date', suffixes = ('','_1y'))
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date_2y', right_on = 'Date', suffixes = ('','_2y'))
df_base = df_base.drop(['Date_6m','Date_1y','Date_2y', 'Ticker_2', 'Ticker_6m', 'Ticker_1y', 'Ticker_2y'], axis = 1)

# Add Original Data
df_base = pd.merge(df_base, df_tickers, how='left', left_on='Ticker', right_on='ticker')
df_base = df_base.drop(["comp_name","pe_ratio_12m","price_per_sales","div_yield","held_by_insiders_pct","held_by_institutions_pct","link"], axis =1)


#%% Calculate returns

# Calculate Return for Equities, SPY, and their Deltas
df_base["Return_6m"] = df_base["Close_6m"]/df_base["Close"]-1
df_base["Return_1y"] = df_base["Close_1y"]/df_base["Close"]-1
df_base["Return_2y"] = df_base["Close_2y"]/df_base["Close"]-1
df_base["Index_6m"] = df_base["SPY_6m"]/df_base["SPY"]-1
df_base["Index_1y"] = df_base["SPY_1y"]/df_base["SPY"]-1
df_base["Index_2y"] = df_base["SPY_2y"]/df_base["SPY"]-1
df_base["Delta_6m"] = df_base["Return_6m"] - df_base["Index_6m"]
df_base["Delta_1y"] = df_base["Return_1y"] - df_base["Index_1y"]
df_base["Delta_2y"] = df_base["Return_2y"] - df_base["Index_2y"]

# Format ROI to float64
df_base["ROI"] = df_base['ROI'].str.replace('%', '')
df_base["ROI"] = df_base["ROI"].astype('float64')
df_base["ROI"] = df_base["ROI"]/100
df_base["ROI"] = df_base["ROI"].round(2)

#%% Export Dataset
df_base.to_csv("master__roi", index = False)