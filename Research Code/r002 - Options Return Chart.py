# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-05

Attempt to plot an options return chart based on inputs
"""


#%% Import Libraries

import matplotlib.pyplot as plt # Using plt over seaborn due to wide data pref
import numpy as np
import pandas as pd
import matplotlib.ticker as mtick



#%% Establish Variables & Conditions

# LONG CALLS
# Stock Info
current_price = 27.52# Current price of the security
strike = 27.5 # Strike price of the option 
premium = 4.25 # Premium issued at the sale of an option at the strike
stock_range_min = 1 # Lowest stock value to model for 
stock_range_max = 100 # Highest stock value to model for 
step = 0.1 # Steps in the calculation



#%% Calculations

buy_hold = []
buy_hold_pct = []
long_call = []
long_call_pct = []
custom_range = np.arange(stock_range_min,stock_range_max,step)

# Return Calculator

for i in custom_range:
    buy_and_hold = 100*(i-current_price)
    buy_and_hold_pct = 100*((i/(current_price))-1)
    buy_hold.append(buy_and_hold)
    buy_hold_pct.append(buy_and_hold_pct)
    if i >= strike:
        lc = 100*(i-(strike+premium))
        lc_pct = 100*((i/strike)-1)
    if i < strike:
        lc = 100*(-premium)
        lc_pct = 100*((0/strike)-1)
    long_call.append(lc)
    long_call_pct.append(lc_pct)

# Create Dataframes
tuplelist = list(zip(custom_range,buy_hold,long_call))
tuplelist_pct = list(zip(custom_range,buy_hold_pct,long_call_pct))

df = pd.DataFrame(tuplelist, columns = ['Stock Price', 'Buy & Hold','Long Calls']) # Not sure of a quicker way to turn lists into a df
df_pct = pd.DataFrame(tuplelist_pct, columns = ['Stock Price', 'Buy & Hold','Long Calls']) # Not sure of a quicker way to turn lists into a df

# Return Charts
plt.figure(dpi=1200)
plt.plot(df['Stock Price'], df['Buy & Hold'], label = "Buy & Hold")
plt.plot(df['Stock Price'], df['Long Calls'], label = "Long Calls")
plt.axhline(0, color='black', linestyle=':') # Line for the 0-return indicator
plt.axvline(current_price, color = 'black', linestyle = ':') # Line for the current price indicator
plt.title('Option Return Chart')
plt.xlabel('Stock Price')
plt.ylabel('Absolute Return')
plt.legend()
plt.yscale('linear') # Can turn to symlog, but hurts readability for others
plt.show()


fig = plt.figure(dpi=1200)
ax = fig.add_subplot(1,1,1)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.plot(df_pct['Stock Price'], df_pct['Buy & Hold'], label = "Buy & Hold")
plt.plot(df_pct['Stock Price'], df_pct['Long Calls'], label = "Long Calls")
plt.axhline(0, color='black', linestyle=':') # Line for the 0-return indicator
plt.axvline(current_price, color = 'black', linestyle = ':') # Line for the current price indicator
plt.title('Option Return Chart (percent)')
plt.xlabel('Stock Price')
plt.ylabel('Percent Return')
plt.legend()
plt.yscale('linear') # Can turn to symlog, but hurts readability for others
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.show()



#%% Appendix


print(df)
"""
# SHORT COVERED CALLS
# Stock Info
current_price = 47.73 # Current price of the security
strike = 25 # Strike price of the option 
premium = 0.47 # Premium issued at the sale of an option at the strike
stock_range_min = 45 # Lowest stock value to model for 
stock_range_max = 60 # Highest stock value to model for 
step = 0.1 # Steps in the calculation
custom_range = np.arange(stock_range_min,stock_range_max,step)
# Return Calculator
buy_hold = []
short_call = []
for i in custom_range:
    buy_and_hold = 100*(i-50.59)
    buy_hold.append(buy_and_hold)
    if i <= strike:
        sc = 100*(premium+i-50.59)
    if i > strike:
        sc = 100*(premium+strike-50.59)
    short_call.append(sc)
# Create Dataframe
tuplelist = list(zip(custom_range,buy_hold,short_call))
df = pd.DataFrame(tuplelist, columns = ['Stock Price', 'Buy & Hold','Short Covered Calls']) # Not sure of a quicker way to turn lists into a df
# Return Chart
plt.plot(df['Stock Price'], df['Buy & Hold'], label = "Buy & Hold")
plt.plot(df['Stock Price'], df['Short Covered Calls'], label = "Short Covered Calls")
plt.axhline(0, color='black', linestyle=':') # Line for the 0-return indicator
plt.axvline(current_price, color = 'black', linestyle = ':') # Line for the current price indicator
plt.title('Option Return Chart')
plt.xlabel('Stock Price')
plt.ylabel('Absolute Return')
plt.legend()
plt.yscale('linear') # Can turn to symlog, but hurts readability for others
plt.show() """