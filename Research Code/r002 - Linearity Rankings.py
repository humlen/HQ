# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-012

A tool to generate a ranking of companies by the linearity of their earnings results
"""

#%% Package Installs
import pandas as pd
from scipy import stats
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import time
import random
from tqdm import tqdm

# Requires Python 3.4+ for relative pathing

#%% Preparations
df_tickers = pd.read_csv("Research Resources/Tickers.csv") 
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


tickerlist = df_tickers["ticker"].to_list()[:100]
companylist = df_tickers["comp_name"].to_list()[:100]


# FOR TESTING PURPOSES ONLY
# tickerlist = ["msft","goog"]
# companylist = ["microsoft","alphabet"]



#%%
"""
                  ═════════•°• ⚠ •°•═════════    
            
                   START OF DATA COLLECTION
                   
                 ═════════•°• ⚠ •°•═════════                
"""

data = []
linearity_list = []

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
        # Collect EPS
        df_eps = pd.read_html(eps)[1]
        df_eps["Ticker"] = ticker
        df_eps.columns= ['Date', 'EPS','Ticker']
        df_eps['Date'] = df_eps['Date'].astype('datetime64')
        df_eps["EPS"] = df_eps['EPS'].str.replace('$', '', regex = False)
        df_eps["EPS"] = df_eps["EPS"].astype('float64')
        df_eps = df_eps.sort_values(by=["Date"])
        df_eps["TTM EPS"] = df_eps["EPS"].rolling(4, min_periods = 4).sum()
        df_eps = df_eps.dropna()
        df_eps = df_eps.reset_index() # Needed to use index as correlation variable
        
        # Calculate Linearity
        data = [[ticker, company, stats.pearsonr(df_eps.index,df_eps["TTM EPS"]).statistic, stats.pearsonr(df_eps.index,df_eps["TTM EPS"]).pvalue, max(df_eps.index)+1]]
        df_linearity = pd.DataFrame(data, columns = ["Ticker", "Company", "Pearson R", "Pearson P-Value", "Number of Quarters"])
        
        # Append
        linearity_list.append(df_linearity)
    
        # Naptime (Only for large data collections [100+ records])
        #sleeptime = random.randint(0,10)
        #time.sleep(sleeptime)
    
    except:
        pass

# Concatenate dataframes
df_base = pd.concat(linearity_list, axis = 0)

 
#%%

"""
                  ═════════•°• ⚠ •°•═════════    
            
                     END OF DATA COLLECTION
                   
                 ═════════•°• ⚠ •°•═════════                
"""


#%% Scored Dataset
dataset = df_base.reset_index(drop=True)
dataset = dataset[dataset["Pearson R"]>0]
# dataset = df_base[df_base.iloc[:,1] > 0]
# dataset = dataset.assign(Score = dataset["Pearson R"]**2 * dataset["Number of Quarters"]**0.5 )
dataset["Score"] = dataset["Pearson R"]**2 * dataset["Number of Quarters"]**0.5
dataset = dataset.sort_values(by=("Score"), ascending = False)

print(dataset.head(20))


#%% Plots


# Plot Variables
# Colors
BG_WHITE = "#fbf9f4"
GREY_LIGHT = "#b4aea9"
GREY50 = "#7F7F7F"
GREY30 = "#4d4d4d"
BLUE_DARK = "#1B2838"
HLINES = [0, 0.5, 0.7]

TICKERS = sorted(dataset["Ticker"].unique())
MARKERS = ["o"] # circle, triangle, square
COLORS = ["#386cb0", "#fdb462", "#7fc97f" ] # A color for each species


fig, ax = plt.subplots(figsize= (14, 10))
fig.patch.set_facecolor(BG_WHITE)
ax.set_facecolor(BG_WHITE)
#plt.figure(dpi=1200)

for h in HLINES:
    ax.axhline(h, color=GREY50, ls=(0, (5, 5)), alpha=0.8, zorder=0)
    
ax.axvline(30, color=GREY50, ls=(0, (5, 5)), alpha=0.8, zorder=0)
    
for ticker, color, marker  in zip(TICKERS, COLORS, MARKERS):
    data = dataset[dataset["Ticker"] == ticker]
    ax.scatter(
        "Number of Quarters", "Pearson R", s=50, color=color, 
        marker=marker, alpha=0.8, data=dataset
    )
    
def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+.5, point['y']+.02, str(point['val']))

label_point(dataset["Number of Quarters"], dataset["Pearson R"], dataset["Ticker"], plt.gca())  

    