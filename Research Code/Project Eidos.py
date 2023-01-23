# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-012

A tool to generate a ranking of companies by the linearity of their earnings results
"""

#%% Package Installs
import pandas as pd
from tqdm import tqdm
from scipy import stats

# How Many Values to display?
n = 50

version_name = "Eidos"
version_number = "1.2"

#%% Preparing Datasets
dataset_eps = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__eps.csv")
dataset_netinc = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__netinc.csv")
df_tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__tickers.csv")


#%% Calculations

    # Calculating Pearson's R for EPS
tickerlist = dataset_eps["Ticker"].unique().tolist()
pearson_list = []

for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    df_pearson_eps = dataset_eps[(dataset_eps["Ticker"] == ticker)]
    df_pearson_eps = df_pearson_eps.reset_index(drop=True)
    try:
        df_pearson_eps = [[ticker, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).statistic, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).pvalue, max(df_pearson_eps.index)+1]]
    except:
        df_pearson_eps = [[ticker,0,0,0]]
        
    df_pearson_eps = pd.DataFrame(df_pearson_eps, columns = ["Ticker", "Pearson R", "Pearson P-Value", "Pearson QNum"])
    pearson_list.append(df_pearson_eps)
 
# Concatenate dataframes
df_eps_pearson = pd.concat(pearson_list, axis = 0)
     
    
    # Calculating Pearson's R for Net Income
tickerlist = dataset_netinc["Ticker"].unique().tolist()
pearson_list = []

for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    df_pearson_ni = dataset_netinc[(dataset_netinc["Ticker"] == ticker)]
    df_pearson_ni = df_pearson_ni.reset_index(drop=True)
    try:
        df_pearson_ni = [[ticker, stats.pearsonr(df_pearson_ni.index,df_pearson_ni["TTM Net Income"]).statistic, stats.pearsonr(df_pearson_ni.index,df_pearson_ni["TTM Net Income"]).pvalue, max(df_pearson_ni.index)+1]]
    except:
        df_pearson_ni = [[ticker,0,0,0]]
    df_pearson_ni = pd.DataFrame(df_pearson_ni, columns = ["Ticker", "Pearson R", "Pearson P-Value", "Pearson QNum"])

    pearson_list.append(df_pearson_ni)
 
# Concatenate dataframes
df_ni_pearson = pd.concat(pearson_list, axis = 0)
   
  
    # Calculating Spearman's Rho for EPS
tickerlist = dataset_eps["Ticker"].unique().tolist()
spearman_list = []

for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    df_spearman_eps = dataset_eps[(dataset_eps["Ticker"] == ticker)]
    df_spearman_eps = df_spearman_eps.reset_index(drop=True)
    try:
        df_spearman_eps = [[ticker, stats.spearmanr(df_spearman_eps.index,df_spearman_eps["TTM EPS"]).statistic, stats.spearmanr(df_spearman_eps.index,df_spearman_eps["TTM EPS"]).pvalue, max(df_spearman_eps.index)+1]]
    except:
        df_spearman_eps = [[ticker,0,0,0]]
    df_spearman_eps = pd.DataFrame(df_spearman_eps, columns = ["Ticker", "Spearman R", "Spearman P-Value", "Spearman QNum"])

    spearman_list.append(df_spearman_eps)
 
# Concatenate dataframes
df_eps_spearman = pd.concat(spearman_list, axis = 0)
     


    # Calculating Spearman's Rho for Net Income
tickerlist = dataset_netinc["Ticker"].unique().tolist()
spearman_list = []

for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    df_spearman_ni = dataset_netinc[(dataset_netinc["Ticker"] == ticker)]
    df_spearman_ni = df_spearman_ni.reset_index(drop=True)
    try:
        df_spearman_ni = [[ticker, stats.spearmanr(df_spearman_ni.index,df_spearman_ni["TTM Net Income"]).statistic, stats.spearmanr(df_spearman_ni.index,df_spearman_ni["TTM Net Income"]).pvalue, max(df_spearman_ni.index)+1]]
    except:
        df_spearman_ni = [[ticker,0,0,0]]
    df_spearman_ni = pd.DataFrame(df_spearman_ni, columns = ["Ticker", "Spearman R", "Spearman P-Value", "Spearman QNum"])

    spearman_list.append(df_spearman_ni)
 
# Concatenate dataframes
df_ni_spearman = pd.concat(spearman_list, axis = 0)


#%%

df_spearman = df_tickers.merge(df_ni_spearman, how = "left", left_on = "ticker", right_on = "Ticker").dropna()
df_spearman = df_spearman[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Spearman R","Spearman P-Value", "Spearman QNum"]]

df_pearson = df_tickers.merge(df_ni_pearson, how = "left", left_on = "ticker", right_on = "Ticker").dropna()
df_pearson = df_pearson[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Pearson R","Pearson P-Value", "Pearson QNum"]]

df_eidos = df_pearson.merge(df_spearman, how ="inner", left_on = "Ticker", right_on = "Ticker", copy = False, suffixes = ("","_copy"))
df_eidos = df_eidos[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Pearson R","Pearson P-Value", "Pearson QNum","Spearman R","Spearman P-Value", "Spearman QNum"]]
df_eidos = df_eidos[df_eidos["Pearson R"]>0]
df_eidos = df_eidos[df_eidos["Spearman R"]>0]
df_eidos = df_eidos[df_eidos["Spearman QNum"]>10]
df_eidos = df_eidos[df_eidos["Pearson P-Value"]<0.1]
df_eidos = df_eidos[df_eidos["Spearman P-Value"]<0.1]

df_eidos["Score MULT"] = df_eidos["Pearson R"] * df_eidos["Spearman R"]
df_eidos["Score MAX"] = df_eidos[["Pearson R","Spearman R"]].max(axis=1)
df_eidos = df_eidos.sort_values(by=("Score MULT"), ascending = False)

df_output = df_eidos.head(n)
df_output = df_output.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

print(df_output)
#%% Plots CURRENTLY BROKEN

"""
# Plot Variables
# Colors
BG_WHITE = "#fbf9f4"
GREY_LIGHT = "#b4aea9"
GREY50 = "#7F7F7F"
GREY30 = "#4d4d4d"
BLUE_DARK = "#1B2838"
HLINES = [0, 0.5, 0.7]

TICKERS = sorted(df_output["Ticker"].unique())
MARKERS = ["o"] # circle, triangle, square
COLORS = ["#386cb0", "#fdb462", "#7fc97f" ] # A color for each species

# Plot 1 - Scatterplot
fig, ax = plt.subplots(figsize= (14, 10))
fig.patch.set_facecolor(BG_WHITE)
ax.set_facecolor(BG_WHITE)
plt.ylim(df_output["Score MULT"].min()-0.01, df_output["Score MULT"].max()+0.01)

for h in HLINES:
    ax.axhline(h, color=GREY50, ls=(0, (5, 5)), alpha=0.8, zorder=0)
    
ax.axvline(0.9, color=GREY50, ls=(0, (5, 5)), alpha=0.8, zorder=0)
    
for ticker, color, marker  in zip(TICKERS, COLORS, MARKERS):
    data = df_output[df_output["Ticker"] == ticker]
    ax.scatter(
        "Score MULT", "Score MAX", s=50, color=color, 
        marker=marker, alpha=0.8, data=df_output,
    )
    
def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+0.6, point['y']+0.002, str(point['val']))

label_point(df_output["Score MAX"], df_output["Score MULT"], df_output["Ticker"], plt.gca())  

# Plot 2 - Linearity Distribution

sns.displot(data=df_output, x="Pearson R", kind="kde", ax=ax)
plt.xlim(0,1)
plt.show()


"""

    