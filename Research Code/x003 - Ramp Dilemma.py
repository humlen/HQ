# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2021-01-05

A friend recently reached out and wanted to know if he should sell his company 
ESPP stock and roll into an ETF, or if he should stick with his stocks for 
another year. 
"""

# Note: ask about long term tax impications for the above.

#%% Import Libraries
import numpy
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

#%% Establish Variables & Conditions

# Model Metrics
iterations = 1000000 # number of simulations

# Stock Metrics
discount = 0.15  #stock price discount for RAMP employees
max_rev_growth = 0.16 # One Std Dev above historical revenue growth YoY
min_rev_growth = 0.05 # One Std Dev below historical revenue growth YoY
price_min = 38.50 # Lowest 52W price
price_max = 87.38 # Highest 52W price
high_ps = 15.47 #historical high P/S of LiveRamp
low_ps = 5.88 # historical low P/S of LiveRamp
outstanding_shares = 68090000 # Currently outstanding shares


#%% Forecast Value

# Create cost basis iterations
cost_basis = []
for i in range(0,iterations):
    n = (1-discount)*min(numpy.random.uniform(price_min,price_max),numpy.random.uniform(price_min,price_max))
    cost_basis.append(n)
    
    
# Create future revenue iterations
future_revenue =[]
# Forecast 1 million 1 year revenue iterations
for i in range(0,iterations):
    rev = 499333000*(1+numpy.random.uniform(max_rev_growth, min_rev_growth))
    future_revenue.append(rev)
    
# Create future P/S ratios
ps = []
for i in range(0,iterations):
    newps = numpy.random.uniform(high_ps,low_ps)
    ps.append(newps)
    
# Sales per share
fv_per_share = numpy.divide(future_revenue,outstanding_shares) 
          
# Price per share   
share_price = numpy.multiply(fv_per_share,ps)

# Return based on cost basis
ramp_returns = numpy.divide(share_price,cost_basis)-1

# Future VUG Returns
mu, sigma = 0.1362, 0.1892 # mean and standard deviation
vug_returns = numpy.random.normal(mu, sigma, iterations)

# Future S&P500 Returns
mu, sigma = 0.0796, 0.1905 # mean and standard deviation
spy_returns = numpy.random.normal(mu, sigma, iterations)

# Label List
list_ramp = []
list_vug = []
list_spy = []

for i in range(0,iterations):
    label_ramp = "RAMP"
    list_ramp.append(label_ramp)
    
    label_vug = "VUG"
    list_vug.append(label_vug)
    
    label_spy = "SPY"
    list_spy.append(label_spy)
  
# i know this probably isnt best practice but i dont have a fancy cs degree get off my back  
df1 = pd.DataFrame(list(zip(ramp_returns,list_ramp)), columns = ["Returns",'Label'])
df2 = pd.DataFrame(list(zip(vug_returns,list_vug)), columns = ["Returns",'Label'])
df3 = pd.DataFrame(list(zip(spy_returns,list_spy)), columns = ["Returns",'Label'])
df4 = df1.append(df2)
returns = df4.append(df3)


# Create Histogram to see distribution of returns vs VUG and SPY
plt.figure(dpi=1200)
sns.histplot(returns, x="Returns", hue="Label", element="step")
plt.axvline(0.08, color = "green")
plt.title("Should Marton sell his RAMP stock")
plt.show()

# Show range of probable returns vs cost basis
plt.figure(dpi=1200)
cost_v_return = pd.DataFrame(list(zip(ramp_returns,cost_basis)), columns = ["Returns",'Cost Basis'])
sns.scatterplot(data=cost_v_return, x="Cost Basis", y="Returns",sizes = 0.1)
plt.axhline(0, color = "black")
plt.show()
print("Finished")