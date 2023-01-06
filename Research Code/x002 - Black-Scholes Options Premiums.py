# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-06

Attempt to calculate options premiums based on greeks
"""

#%% Import Libraries

import yfinance as yf
import pandas as pd
import numpy as np
from math import log, sqrt, pi, exp
from scipy.stats import norm
from datetime import datetime, date
from pandas import DataFrame


# Test selling OTM covered calls against highly liquid ETFs, to squeeze extra alpha out of what is meant to 
# be a less volatile "stable" addition to your portfolio

# We will be using a variation of the Black-Scholes method to simulate options pricing, and simulate this for 0.5 standard
# deviations above 30 day fluctuations. For this test we will use SPY. This means that we have to go through a 
# multi-step process of 
# 1. Get the standard deviation of the last 30 days of SPY data
# 2. Generate an options premium based on Black-Scholes theorem for a sold call 30 STD.DEV above current
# 3. Check if call is exercised 30 days after purchase.
# 4. Calculate 30-day return whether the call was exercised or not
# 5. Repeat from 1 Jan 2000 to current date

#%% Establish Variables & Conditions

# Base variables
startdate = "2020-12-31" #First Date of investment
option_duration = 28


# Base Conditions
enddate = pd.to_datetime(startdate) + pd.DateOffset(days=option_duration) # Option Expiry. 28 days so it always lands on a weekday
data = yf.download("SPY", start=startdate, end=enddate).iloc[:,[3]]
df = pd.DataFrame(data)
df = df.assign(close_day_before = df.shift(1)) # adds lag 1 
df.columns = ["Close","close_day_before"]
df['returns'] = ((df.Close - df.close_day_before)/df.close_day_before)
sigma = np.sqrt(252) * df['returns'].std()
price_i = df.Close[0] # Price at beginning of period
price_f = df.Close[-1] # Price at end of period 
T = 28/365 # Fraction of year of option time
r = 0.005 # Risk-free rate. Placeholder for now, use TNX eventually
k = price_f*(1+0.5*sigma*sqrt(28/365)) # Strike price


print('Write date is:',startdate)
print('Expiry is:',enddate)
print('Price is:',price_i)
print('Strike Price is:',k)
print('Time is:',T)
print('Risk-Free Rate is:',r)
print('Sigma is:',sigma)
print( )

#%% Calculation

# Black-Scholes calculation for option premium
    # C = Option Cost
    # N = CDF of the normal distribution
    # price_f = spot price of an asset
    # k = strike price
    # r = risk free intrest rate
    # T = time to maturity
    # sigma = volatility of the asset
    # C = N(d1)price_f - N(d2)Ke^-rt
    # d1 = (ln(price_f/K)+(r+sigma^2/2)t/(sigma*sq(t)))
    # d2 = d1-sigma*sq(t)

def d1(price_i,k,T,r,sigma):
    return(log(price_i/k)+(r+sigma**2/2.)*T)/(sigma*sqrt(T))

def d2(price_i,k,T,r,sigma):
    return d1(price_i,k,T,r,sigma)-sigma*sqrt(T)

# Calculating call premiums
def bs_call(price_i,k,T,r,sigma):
    return price_i*norm.cdf(d1(price_i,k,T,r,sigma))-k*exp(-r*T)*norm.cdf(d2(price_i,k,T,r,sigma))

print('The Option Price is: ', round(bs_call(price_i, k, T, r, sigma),2))