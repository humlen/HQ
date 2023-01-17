# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-012

A tool to generate a ranking of companies by the linearity of their earnings results
"""

#%% Package Installs
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# How Many Values to display?
n = 50

version_name = "Linearity"
version_number = "1.00"

#%% Scored Dataset
dataset = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__linearity.csv")
df_tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__tickers.csv")
dataset = dataset.reset_index(drop=True)
dataset = dataset[dataset["Pearson R"]>0]
dataset["f_numquart"] = dataset["Number of Quarters"] / dataset["Number of Quarters"].max()
# dataset = df_base[df_base.iloc[:,1] > 0]
# dataset = dataset.assign(Score = dataset["Pearson R"]**2 * dataset["Number of Quarters"]**0.5 )
dataset["Score"] = dataset["Pearson R"]**2 * dataset["f_numquart"]**0.5
dataset = pd.merge(dataset, df_tickers, how="left", left_on="Ticker", right_on="ticker")
dataset = dataset.sort_values(by=("Score"), ascending = False)

output_list = dataset[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Score", "pe_ratio_12m"]].head(50)
output_list = output_list.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry","pe_ratio_12m":"P/E"}).reset_index(drop=True)
output_plot = dataset.head(n)

#%% Plots


# Plot Variables
# Colors
BG_WHITE = "#fbf9f4"
GREY_LIGHT = "#b4aea9"
GREY50 = "#7F7F7F"
GREY30 = "#4d4d4d"
BLUE_DARK = "#1B2838"
HLINES = [0, 0.5, 0.7]

TICKERS = sorted(output_list["Ticker"].unique())
MARKERS = ["o"] # circle, triangle, square
COLORS = ["#386cb0", "#fdb462", "#7fc97f" ] # A color for each species

# Plot 1 - Scatterplot
fig, ax = plt.subplots(figsize= (14, 10))
fig.patch.set_facecolor(BG_WHITE)
ax.set_facecolor(BG_WHITE)
plt.ylim(output_list["Score"].min()-0.01, output_list["Score"].max()+0.01)

for h in HLINES:
    ax.axhline(h, color=GREY50, ls=(0, (5, 5)), alpha=0.8, zorder=0)
    
ax.axvline(25, color=GREY50, ls=(0, (5, 5)), alpha=0.8, zorder=0)
    
for ticker, color, marker  in zip(TICKERS, COLORS, MARKERS):
    data = output_list[output_list["Ticker"] == ticker]
    ax.scatter(
        "P/E", "Score", s=50, color=color, 
        marker=marker, alpha=0.8, data=output_list,
    )
    
def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+0.6, point['y']+0.002, str(point['val']))

label_point(output_list["P/E"], output_list["Score"], output_list["Ticker"], plt.gca())  

# Plot 2 - Linearity Distribution

sns.displot(data=dataset, x="Pearson R", kind="kde", ax=ax)
plt.xlim(0,1)
plt.show()



print(output_list)

    