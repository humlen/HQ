# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-012

A tool to generate a ranking of companies by the linearity of their earnings results
"""

#%% Package Installs
import pandas as pd
import matplotlib.pyplot as plt


#%% Scored Dataset
dataset = pd.read_csv("Database/master__linearity.csv")
dataset = dataset.reset_index(drop=True)
dataset = dataset[dataset["Pearson R"]>0]
# dataset = df_base[df_base.iloc[:,1] > 0]
# dataset = dataset.assign(Score = dataset["Pearson R"]**2 * dataset["Number of Quarters"]**0.5 )
dataset["Score"] = dataset["Pearson R"]**2 * dataset["Number of Quarters"]**0.5
dataset = dataset.sort_values(by=("Score"), ascending = False)

dataset = dataset.head(50)

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

print(dataset)

    