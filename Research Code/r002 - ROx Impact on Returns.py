# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-06

This research document aims to investigate the impact ROA / ROE / ROI / ROIC 
have on future performances of stocks.
"""

#%% Package Installs
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.stats import pearsonr


# SNS
sns.set_style("white")


# Only enable if you know what you're doing
import warnings 
warnings.filterwarnings("ignore")

#%% Normalize Dataset

dataset = pd.read_csv("Database/master__roi.csv")
dataset = dataset.replace([np.inf, -np.inf], np.nan).dropna(axis=0)

# Set target
variable = "ROI"
target = "Delta_6m"

# Filter Sector
# sectors = ["Construction"]
# df_base_filtered = df_base_filtered[df_base_filtered["sector"].isin(sectors)]

# Remove Outlier ROIs
roi_low = dataset[variable].quantile(0.025)
roi_high  = dataset[variable].quantile(0.975)
dataset = dataset[(dataset[variable] < roi_high) & (dataset[variable] > roi_low)]

# Remove Outlier Returns
ret_low = dataset[target].quantile(0.025)
ret_high  = dataset[target].quantile(0.975)
dataset = dataset[(dataset[target] < ret_high) & (dataset[target] > ret_low)]

 #%% Plots


# Density Plot of ROA vs Delta 1Y
plt.figure(dpi=1200)
sns.kdeplot(data = dataset, x=variable, y=target, cmap="Blues", shade=True)
plt.title("ROI and Performance Distribution, {}".format(target))
#graph.set_ylabel("Return vs S&P500, 1Y later")
plt.axhline(y=0, color = 'black', linestyle = '--', lw = .3) # Net Zero
plt.axvline(x=0, color = 'black', linestyle = '--', lw = .3) # Net Zero
plt.show()

# Line Chart with average Performance per Year
plt.figure(dpi=1200)
graph = sns.lineplot(data=dataset, x="Date", y=target, ci =95)
graph.axhline(y=0, color = 'black', linestyle = '--', lw = 1) # Net Zero
graph.set_title("Relative Return vs Market avg., {}".format(target))
graph.set_ylabel("% Return, 1Y Later")
graph.set(xlabel=None)
plt.show()

# Line Chart with ROA (/w Confidence Interval) and Relative Market Outperformance
plt.figure(dpi=1200)
sns.lineplot(data=dataset, x=variable, y=target, ci=95)
plt.axhline(y=0, color = 'black', linestyle = '--', lw = .3) # Net Zero
plt.axvline(x=0, color = 'black', linestyle = '--', lw = .3) # Net Zero
plt.title("ROA and Performance Distribution, {}".format(target))
plt.ylabel("Return vs S&P500, 1Y later")
plt.show()


#%% Correlation Ranker

corr, _ = pearsonr(dataset["ROI"],dataset["Return_6m"])
print("Pearsons Correlation (6m return): %.3f" % corr)

corr, _ = pearsonr(dataset["ROI"],dataset["Return_1y"])
print("Pearsons Correlation (1y return): %.3f" % corr)

corr, _ = pearsonr(dataset["ROI"],dataset["Return_2y"])
print("Pearsons Correlation (2y return): %.3f" % corr)


#%% Correlation Ranker
df_sectors = dataset.sector.unique()
sectorlist = df_sectors.tolist()
    
correlation_rank = []
correlation_rank_columns = ["Sector","Metric","Score"]
for i in tqdm(range(len(sectorlist))):
    sector = sectorlist[i]
    corr_r6m, _ = pearsonr(dataset["ROI"],dataset["Return_6m"])
    corr_r1y, _ = pearsonr(dataset["ROI"],dataset["Return_1y"])
    corr_r2y, _ = pearsonr(dataset["ROI"],dataset["Return_2y"])
    corr_d6m, _ = pearsonr(dataset["ROI"],dataset["Delta_6m"])
    corr_d1y, _ = pearsonr(dataset["ROI"],dataset["Delta_1y"])
    corr_d2y, _ = pearsonr(dataset["ROI"],dataset["Delta_2y"])
    correlation_rank.append([sector, 'corr_r6m', corr_r6m])
    correlation_rank.append([sector, 'corr_r1y', corr_r1y])
    correlation_rank.append([sector, 'corr_r2y', corr_r2y])
    correlation_rank.append([sector, 'corr_d6m', corr_d6m])
    correlation_rank.append([sector, 'corr_d1y', corr_d1y])
    correlation_rank.append([sector, 'corr_d2y', corr_d2y])


df_correlation_rank = pd.DataFrame(correlation_rank, columns = correlation_rank_columns)
df_correlation_rank = df_correlation_rank.sort_values(by=["Score"], ascending = False)
print(df_correlation_rank)