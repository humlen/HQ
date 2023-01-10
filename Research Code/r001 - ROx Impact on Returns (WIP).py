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
import seaborn as sns
import matplotlib.pyplot as plt

# SNS
sns.set_style("white")


# Only enable if you know what you're doing
import warnings 
warnings.filterwarnings("ignore")


#%% Preparations

df_tickers = pd.read_csv("../Research Resources/Tickers.csv") #1036 Entries
df_tickers = df_tickers.drop_duplicates(subset=["ticker"])
tickerlist = df_tickers["ticker"].to_list()
companylist = df_tickers["comp_name"]
start_date = '2010-01-01'
end_date = datetime.now()+timedelta(days=-730)
list_roa = []
list_prices = []
mt =  "https://www.macrotrends.net/stocks/charts/"

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

  # Append to list of dataframes
  list_prices.append(df_price)
  
df_prices = pd.concat(list_prices, axis = 0) 

#%% YFinance Target Index Price Collection

spy_data = yf.Ticker("SPY")
spy_hist = spy_data.history(period="max")
df_spy = spy_hist[["Close"]]
df_spy["Ticker"] = '"SPY"'
df_spy.reset_index(inplace=True)
df_spy.columns= ['Date','SPY','Ticker']
df_spy = df_spy[(df_spy['Date'] >= start_date)]
#df_dates2 = pd.DataFrame({'Date':pd.date_range(start=start_date, end=datetime.today())})
df_spy = pd.merge(df_dates, df_spy, how = 'left', left_on='Date', right_on = 'Date')
df_spy = df_spy.ffill(axis=0)
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
#df_base = df_base.drop(['Date_6m','Date_1y','Date_2y'], axis = 1)

#%% Add SPY prices to table




df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date', right_on = 'Date', suffixes = ('','_2'))
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date_6m', right_on = 'Date', suffixes = ('','_6m'))
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date_1y', right_on = 'Date', suffixes = ('','_1y'))
df_base = pd.merge(df_base,df_spy, how = 'left', left_on='Date_2y', right_on = 'Date', suffixes = ('','_2y'))

df_base = df_base.drop(['Date_6m','Date_1y','Date_2y', 'Ticker_2', 'Ticker_6m', 'Ticker_1y', 'Ticker_2y'], axis = 1)


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

# Format ROA to float64
df_base["ROA"] = df_base['ROA'].str.replace('%', '')
df_base["ROA"] = df_base["ROA"].astype('float64')
df_base["ROA"] = df_base["ROA"]/100
df_base["ROA"] = df_base["ROA"].round(2)

df_base.info()
df_base.dropna()
df_base.info()
 

#%% Normalize Dataset

# Set target
variable = "ROA"
target = "Delta_6m"
comparison = "Index_6m"



# Remove Outlier Dates
df_base_filtered = df_base[(df_base["Date"] >= start_date)]

# Remove Outlier ROAs
roa_low = df_base_filtered[variable].quantile(0.01)
roa_high  = df_base_filtered[variable].quantile(0.99)
df_base_filtered = df_base_filtered[(df_base_filtered[variable] < roa_high) & (df_base_filtered[variable] > roa_low)]

# Remove Outlier Returns
ret_low = df_base_filtered[target].quantile(0.01)
ret_high  = df_base_filtered[target].quantile(0.99)
df_base_filtered = df_base_filtered[(df_base_filtered[target] < ret_high) & (df_base_filtered[target] > ret_low)]

#%% Plots


# Density Plot of ROA vs Delta 1Y
plt.figure(dpi=1200)
sns.kdeplot(data = df_base_filtered, x=variable, y=target, cmap="Blues", shade=True)
plt.title("ROA and Performance Distribution")
#graph.set_ylabel("Return vs S&P500, 1Y later")
plt.axhline(y=0, color = 'black', linestyle = '--', lw = .3) # Net Zero
plt.axvline(x=0, color = 'black', linestyle = '--', lw = .3) # Net Zero
plt.show()

# Line Chart with average Performance per Year
plt.figure(dpi=1200)
graph = sns.lineplot(data=df_base, x="Date", y=target, ci =95)
graph.axhline(y=0, color = 'black', linestyle = '--', lw = 1) # Net Zero
graph.set_title("Relative Return vs Market avg.")
graph.set_ylabel("% Return, 1Y Later")
graph.set(xlabel=None)
plt.show()

#%% WIP

# Line Chart with ROA (/w Confidence Interval) and Relative Market Outperformance
#plt.figure(dpi=1200)
sns.lineplot(data=df_base_filtered, x="ROA", y="Delta_1y", ci=95)
plt.axhline(y=0, color = 'black', linestyle = '--', lw = 1) # Net Zero
#mean_y = df_base_filtered["Delta_1y"].mean()
# plt.axhline(y=mean_y, color = 'orange', linestyle = '--', lw = 1) # Dataset Mean
plt.title("ROA and Performance Distribution")
plt.ylabel("Return vs S&P500, 1Y later")



#%%

sns.jointplot(x=df_base_filtered.ROA, y=df_base_filtered.Return_6m, cmap="Blues", shade=True, kind='kde')
plt.axhline(y=0)





