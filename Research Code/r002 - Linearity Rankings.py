# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-012

A tool to generate a ranking of companies by the linearity of their earnings results
"""

#%% Package Installs
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import time
import random
from tqdm import tqdm

#%% Preparations
df_tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Research Code/Research Resources/Tickers.csv") 
df_tickers = df_tickers.drop_duplicates(subset=["comp_name"])
start_date = '2010-01-01'
list_eps = []
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


""" While Testing
tickerlist = df_tickers["ticker"].to_list()
companylist = df_tickers["comp_name"].to_list()
"""

tickerlist = ["msft","aapl","goog","meta"]
companylist = ["microsoft","apple","alphabet","meta-platforms"]



#%%
"""
                  ═════════•°• ⚠ •°•═════════    
            
                   START OF DATA COLLECTION
                   
                 ═════════•°• ⚠ •°•═════════                
"""


# Loop through list elements to collect data
print("Be patient, this will take some time...")
for i in tqdm(range(len(tickerlist))):

    # Collect Ticker
    ticker = tickerlist[i]
    # Collect Company Name
    company = companylist[i]
    # Get ROI-table from Macrotrends
    eps = "{base}{ticker}/{company}/eps-earnings-per-share-diluted".format(ticker=ticker,company=company,base=mt)
    # Remake into a dataframe
    try:
        df_eps = pd.read_html(eps)[1]
        df_eps["Ticker"] = ticker
        df_eps['Date'] = df_eps['Date'].astype('datetime64')
        df_eps["EPS"] = df_eps['EPS'].str.replace('$', '', regex = False)
        df_eps["EPS"] = df_eps["EPS"].astype('float64')
        df_eps["Linearity"] = df_eps
        df_eps.columns= ['Date', 'EPS','Ticker']

        list_eps.append(df_eps)
   
    # Naptime
    #sleeptime = random.randint(0,10)
    #time.sleep(sleeptime)
    
    except:
        pass



  # Append to list of dataframes
  

# Concatenate dataframes
df_base = pd.concat(list_eps, axis = 0)


#%%

"""
                  ═════════•°• ⚠ •°•═════════    
            
                     END OF DATA COLLECTION
                   
                 ═════════•°• ⚠ •°•═════════                
"""