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

# Needs to be fixed: read from CSV
tickerlist = ['msft','aapl','goog','amzn','meta','nflx']
companylist = ['microsoft','apple','alphabet','amazon','meta-platforms','netflix']
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
 
#%% Plot
# libraries & dataset

# Add thresh parameter
plt.figure(dpi=1200)
sns.kdeplot(x=df_base.ROA, y=df_base.Delta_6m, cmap="Blues", shade=True, thresh=0)
plt.show()

# Add line with confidence interval
plt.figure(dpi=1200)
graph = sns.lineplot(data=df_base, x="ROA", y="Delta_6m", ci=95)
graph.axhline(y=0, color = 'black', linestyle = '--', lw = 1)
#graph.axhline(y=0.08, color = 'green', linestyle = '--', lw = 1)

# LOL
plt.figure(dpi=1200)
graph = sns.lineplot(data=df_base, x="ROA", y="Return_6m", ci=95)
graph.axhline(y=0, color = 'black', linestyle = '--', lw = 1)
graph.axhline(y=0.08, color = 'green', linestyle = '--', lw = 1)


"""
Works, but IDK how to tweak
y_mean = df_base.groupby('ROA').mean()['Delta_6m']
x = y_mean.index

# Compute upper and lower bounds using chosen uncertainty measure: here
# it is a fraction of the standard deviation of measurements at each
# time point based on the unbiased sample variance
y_std = df_base.groupby('ROA').std()['Delta_6m']
error = 0.5*y_std
lower = y_mean - error
upper = y_mean + error

# Draw plot with error band and extra formatting to match seaborn style
fig, ax = plt.subplots(figsize=(9,5))
#ax.figure(dpi=1200)
ax.plot(x, y_mean, label='Delta_6m mean')
ax.plot(x, lower, color='tab:blue', alpha=0.1)
ax.plot(x, upper, color='tab:blue', alpha=0.1)
ax.fill_between(x, lower, upper, alpha=0.2)
ax.set_xlabel('ROA')
ax.set_ylabel('Delta 6M')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.hlines(y=0)
#ax.axhline(y=0, color = 'black', linestype = '-')
#ax.axhline(y=0.08, color = 'green', linestype = '--')
plt.show()
"""

