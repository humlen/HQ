# -*- coding: utf-8 -*-
"""
@author: eirik
@date: 2023-01-13

A tool to collect basic information about a company, and export it in a format
compatible with a premade PowerBI-Report
"""

#%% Package Installs
import pandas as pd
import yfinance as yf
import numpy as np
import warnings
from bs4 import BeautifulSoup 
from urllib.request import Request, urlopen
import time
import requests
import json
from datetime import datetime

# Caveats and config
warnings.filterwarnings("ignore")



#%% Config
# Config
# Name & Version
version_name = "BDR"
version_number = "3.0.0"
color_open = "\x1b["
color_close = "\x1b[0m"
color_green = "0;32;40m"
color_orange = "0;33;40m"
color_red = "0;31;40m"
color_blue = "0;34;40m"
color_white = "0;37;40m"
color_special_command = "3;37;40m"

print("Booting "+version_name+" v "+version_number+"...")


print(
"""
======================================================================================================="""+color_open+color_green+"""

8888888b.                   d8b                   888              888888b.   8888888b.  8888888b.  
888   Y88b                  Y8P                   888              888  "88b  888  "Y88b 888   Y88b 
888    888                                        888              888  .88P  888    888 888    888 
888   d88P 888d888 .d88b.  8888  .d88b.   .d8888b 888888           8888888K.  888    888 888   d88P 
8888888P"  888P"  d88""88b "888 d8P  Y8b d88P"    888              888  "Y88b 888    888 8888888P"  
888        888    888  888  888 88888888 888      888              888    888 888    888 888 T88b   
888        888    Y88..88P  888 Y8b.     Y88b.    Y88b.            888   d88P 888  .d88P 888  T88b  
888        888     "Y88P"   888  "Y8888   "Y8888P  "Y888           8888888P"  8888888P"  888   T88b 
                            888  """   +color_close+"""                      
======================== """+color_open+color_green+"  d88P  "+color_close+"""======================================================================                             
                         """+color_open+color_green+"888P"+color_close+"\n")

 
#%% 

# Menu Items
menu_item_1 = input("What ticker would you like to retrieve data for?\n")

#%% Inputs
ticker = menu_item_1
start_time = time.time()

#%% Preparations
ticker = ticker.upper()
yf_ticker = yf.Ticker(ticker)
start_date = "2010-01-01"
master_tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__tickers.csv") 
meta_stock = master_tickers.loc[master_tickers['ticker'] == ticker]
company = meta_stock["comp_name"].values
company = np.array2string(company).replace("[","").replace("]","").replace("'","").replace('"','')
company_beaut = meta_stock["comp_name_2"].values
company_beaut = np.array2string(company_beaut).replace("[","").replace("]","").replace("'","")
print ('Getting data for ' + company_beaut + '...\n')

# Resources
mt =                "https://www.macrotrends.net/stocks/charts/"
fv =                "https://finviz.com/quote.ashx?t={ticker}&p=d".format(ticker=ticker)
fcf =               "{base}{ticker}/{company}/free-cash-flow".format(ticker=ticker,company=company,base=mt)
roe =               "{base}{ticker}/{company}/roe".format(ticker=ticker,company=company,base=mt)
roi =               "{base}{ticker}/{company}/roi".format(ticker=ticker,company=company,base=mt)
roa =               "{base}{ticker}/{company}/roa".format(ticker=ticker,company=company,base=mt)
grossmarg =         "{base}{ticker}/{company}/gross-margin".format(ticker=ticker,company=company,base=mt)
opermarg =          "{base}{ticker}/{company}/operating-margin".format(ticker=ticker,company=company,base=mt)
netmarg =           "{base}{ticker}/{company}/net-profit-margin".format(ticker=ticker,company=company,base=mt)
rnd =               "{base}{ticker}/{company}/research-development-expenses".format(ticker=ticker,company=company,base=mt)

# ADDED v1.0
cash =              "{base}{ticker}/{company}/cash-on-hand".format(ticker=ticker,company=company,base=mt)
debt =              "{base}{ticker}/{company}/long-term-debt".format(ticker=ticker,company=company,base=mt)

# Added v 3.0
incomestatement =   "{base}{ticker}/{company}/income-statement?freq=Q".format(ticker=ticker,company=company,base=mt)
balancesheet =      "{base}{ticker}/{company}/balance-sheet?freq=Q".format(ticker=ticker,company=company,base=mt)
cashflowstatement = "{base}{ticker}/{company}/cash-flow-statement?freq=Q".format(ticker=ticker,company=company,base=mt)

#%% Income Statement
html = requests.get(incomestatement)
soup = BeautifulSoup(html.text, 'html.parser')
htmltext = soup.prettify()

varlist = {}
vars  = htmltext.split("var ")[1:]  # get each var entry
for v in vars:
    name = v.split("=")[0].strip()  # first part is the var [name = "]
    try:
        value = v.split("originalData = ")[1]        # second part is the value [ = "..."]
        value = value.replace(";","")
    except:
        value = 0
    varlist[name] = value           # store it for printing below           

originalData = varlist["originalData"]

# Data Formatting - Income Statement
data = json.loads(originalData)
df_IncomeStatement = pd.DataFrame.from_dict(data)
df_IncomeStatement["field_name"] = df_IncomeStatement["field_name"].str.split(">").str[1]
df_IncomeStatement["field_name"] = df_IncomeStatement["field_name"].str.split("<").str[0]
df_IncomeStatement = df_IncomeStatement.drop(["popup_icon"], axis = 1)
df_IncomeStatement = df_IncomeStatement.rename(columns = {'field_name':'Date'})
df_IncomeStatement.index = df_IncomeStatement["Date"]
df_IncomeStatement = df_IncomeStatement.drop(["Date"], axis = 1)
df_IncomeStatement = df_IncomeStatement.T
df_IncomeStatement = df_IncomeStatement.reset_index()
df_IncomeStatement = df_IncomeStatement.rename(columns = {'index':'Date'})

# Calculated Values
df_IncomeStatement = df_IncomeStatement.sort_values(by=["Date"])

    # Revenue
df_IncomeStatement["Revenue"] = df_IncomeStatement["Revenue"].replace("",0)
df_IncomeStatement["Revenue"] = df_IncomeStatement["Revenue"].astype("float64")
df_IncomeStatement["Revenue"] = df_IncomeStatement["Revenue"] * 1000000
df_IncomeStatement["Revenue - QoQ"] = df_IncomeStatement["Revenue"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["Revenue - YoY"] = df_IncomeStatement["Revenue"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["Revenue TTM"] = df_IncomeStatement["Revenue"].rolling(4).sum() 
df_IncomeStatement["Revenue TTM - QoQ"] = df_IncomeStatement["Revenue TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["Revenue TTM - YoY"] = df_IncomeStatement["Revenue TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["Revenue TTM - 5Y CAGR"]  = ((df_IncomeStatement['Revenue TTM'].pct_change(20)+1)**0.2)-1
df_IncomeStatement["Revenue TTM - 5Y CAGR"] = df_IncomeStatement["Revenue TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)
    # SG&A Metrics
df_IncomeStatement["SG&A Expenses"] = df_IncomeStatement["SG&A Expenses"].replace("",0)
df_IncomeStatement["SG&A Expenses"] = df_IncomeStatement["SG&A Expenses"].astype("float64")
df_IncomeStatement["SG&A Expenses"] = df_IncomeStatement["SG&A Expenses"] * 1000000
df_IncomeStatement["SG&A TTM"] = df_IncomeStatement["SG&A Expenses"].rolling(4).sum()
df_IncomeStatement["SG&A Percentage of Revenue"] = df_IncomeStatement["SG&A TTM"]/df_IncomeStatement["Revenue TTM"]
df_IncomeStatement["SG&A Percentage of Revenue - QoQ"] = df_IncomeStatement["SG&A Percentage of Revenue"].pct_change(1)
df_IncomeStatement["SG&A Percentage of Revenue - YoY"] = df_IncomeStatement["SG&A Percentage of Revenue"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["SG&A Percentage of Revenue - 5Y CAGR"]  = ((df_IncomeStatement['SG&A Percentage of Revenue'].pct_change(20)+1)**0.2)-1
df_IncomeStatement["SG&A Percentage of Revenue - 5Y CAGR"] = df_IncomeStatement["SG&A Percentage of Revenue - 5Y CAGR"].replace([np.inf,-np.inf],0)

    # Net Income
df_IncomeStatement["Net Income"] = df_IncomeStatement["Net Income"].replace("",0)
df_IncomeStatement["Net Income"] = df_IncomeStatement["Net Income"].astype("float64")
df_IncomeStatement["Net Income"] = df_IncomeStatement["Net Income"] * 1000000
df_IncomeStatement["Net Income - QoQ"] = df_IncomeStatement["Net Income"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["Net Income - YoY"] = df_IncomeStatement["Net Income"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["Net Income TTM"] = df_IncomeStatement["Net Income"].rolling(4).sum() 
df_IncomeStatement["Net Income TTM - QoQ"] = df_IncomeStatement["Net Income TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["Net Income TTM - YoY"] = df_IncomeStatement["Net Income TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["Net Income TTM - 5Y CAGR"]  = ((df_IncomeStatement['Net Income TTM'].pct_change(20)+1)**0.2)-1
df_IncomeStatement["Net Income TTM - 5Y CAGR"] = df_IncomeStatement["Net Income TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)

    # EBITDA
df_IncomeStatement["EBITDA"] = df_IncomeStatement["EBITDA"].replace("",0)
df_IncomeStatement["EBITDA"] = df_IncomeStatement["EBITDA"].astype("float64")
df_IncomeStatement["EBITDA"] = df_IncomeStatement["EBITDA"] * 1000000
df_IncomeStatement["EBITDA - QoQ"] = df_IncomeStatement["EBITDA"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["EBITDA - YoY"] = df_IncomeStatement["EBITDA"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["EBITDA TTM"] = df_IncomeStatement["EBITDA"].rolling(4).sum() 
df_IncomeStatement["EBITDA TTM - QoQ"] = df_IncomeStatement["EBITDA TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["EBITDA TTM - YoY"] = df_IncomeStatement["EBITDA TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["EBITDA TTM - 5Y CAGR"]  = ((df_IncomeStatement['EBITDA TTM'].pct_change(20)+1)**0.2)-1   
df_IncomeStatement["EBITDA TTM - 5Y CAGR"] = df_IncomeStatement["EBITDA TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)

    # Shares Outstanding
df_IncomeStatement["Shares Outstanding"] = df_IncomeStatement["Shares Outstanding"].replace("",0) 
df_IncomeStatement["Shares Outstanding"] = df_IncomeStatement["Shares Outstanding"].astype("float64")
df_IncomeStatement["Shares Outstanding"] = df_IncomeStatement["Shares Outstanding"] * 1000000
df_IncomeStatement["Shares Outstanding - QoQ"] = df_IncomeStatement["Shares Outstanding"].pct_change(1) .replace([np.inf,-np.inf],0)
df_IncomeStatement["Shares Outstanding - YoY"] = df_IncomeStatement["Shares Outstanding"].pct_change(4).replace([np.inf,-np.inf],0) 
df_IncomeStatement["Shares Outstanding - 5Y CAGR"] = ((df_IncomeStatement['Shares Outstanding'].pct_change(20)+1)**0.2)-1    
df_IncomeStatement["Shares Outstanding - 5Y CAGR"] = df_IncomeStatement["Shares Outstanding - 5Y CAGR"].replace([np.inf,-np.inf],0)

    # EPS
df_IncomeStatement["EPS - Earnings Per Share"] = df_IncomeStatement["EPS - Earnings Per Share"].replace("",0)
df_IncomeStatement["EPS - Earnings Per Share"] = df_IncomeStatement["EPS - Earnings Per Share"].astype("float64")
df_IncomeStatement["EPS - QoQ"] = df_IncomeStatement["EPS - Earnings Per Share"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["EPS - YoY"] = df_IncomeStatement["EPS - Earnings Per Share"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["EPS TTM"] = df_IncomeStatement["EPS - Earnings Per Share"].rolling(4).sum() 
df_IncomeStatement["EPS TTM - QoQ"] = df_IncomeStatement["EPS TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["EPS TTM - YoY"] = df_IncomeStatement["EPS TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["EPS TTM - 5Y CAGR"]  = ((df_IncomeStatement['EPS TTM'].pct_change(20)+1)**0.2)-1  
df_IncomeStatement["EPS TTM - 5Y CAGR"] = df_IncomeStatement["EPS TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)
 

    # Operating Expenses
df_IncomeStatement["Operating Expenses"] = df_IncomeStatement["Operating Expenses"].replace("",0)
df_IncomeStatement["Operating Expenses"] = df_IncomeStatement["Operating Expenses"].astype("float64")
df_IncomeStatement["Operating Expenses"] = df_IncomeStatement["Operating Expenses"] * 1000000
df_IncomeStatement["Operating Expenses - QoQ"] = df_IncomeStatement["Operating Expenses"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["Operating Expenses - YoY"] = df_IncomeStatement["Operating Expenses"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["Operating Expenses TTM"] = df_IncomeStatement["Operating Expenses"].rolling(4).sum() 
df_IncomeStatement["Operating Expenses TTM - QoQ"] = df_IncomeStatement["Operating Expenses TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_IncomeStatement["Operating Expenses TTM - YoY"] = df_IncomeStatement["Operating Expenses TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_IncomeStatement["Operating Expenses TTM - 5Y CAGR"]  = ((df_IncomeStatement['Operating Expenses TTM'].pct_change(20)+1)**0.2)-1   
df_IncomeStatement["Operating Expenses TTM - 5Y CAGR"] = df_IncomeStatement["Operating Expenses TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)
    # Revenue / Net Income
df_IncomeStatement["Revenue / Net Income"] = df_IncomeStatement["Revenue TTM"]/df_IncomeStatement["Net Income TTM"]
df_IncomeStatement["Revenue / Net Income Lower Quintile"] = df_IncomeStatement["Revenue / Net Income"].quantile(.2)
df_IncomeStatement["Revenue / Net Income Upper Quintile"] = df_IncomeStatement["Revenue / Net Income"].quantile(.8)


#%% Balance Sheet
html = requests.get(balancesheet)
soup = BeautifulSoup(html.text, 'html.parser')
htmltext = soup.prettify()

varlist = {}
vars  = htmltext.split("var ")[1:]  # get each var entry
for v in vars:
    name = v.split("=")[0].strip()  # first part is the var [name = "]
    try:
        value = v.split("originalData = ")[1]        # second part is the value [ = "..."]
        value = value.replace(";","")
    except:
        value = 0
    varlist[name] = value           # store it for printing below        
    
originalData = varlist["originalData"]

# Data Formatting - Income Statement
data = json.loads(originalData)
df_BalanceSheet = pd.DataFrame.from_dict(data)
df_BalanceSheet["field_name"] = df_BalanceSheet["field_name"].str.split(">").str[1]
df_BalanceSheet["field_name"] = df_BalanceSheet["field_name"].str.split("<").str[0]
df_BalanceSheet = df_BalanceSheet.drop(["popup_icon"], axis = 1)
df_BalanceSheet = df_BalanceSheet.rename(columns = {'field_name':'Date'})
df_BalanceSheet.index = df_BalanceSheet["Date"]
df_BalanceSheet = df_BalanceSheet.drop(["Date"], axis = 1)
df_BalanceSheet = df_BalanceSheet.T
df_BalanceSheet = df_BalanceSheet.reset_index()
df_BalanceSheet = df_BalanceSheet.rename(columns = {'index':'Date'})

# Calculated Values
df_BalanceSheet = df_BalanceSheet.sort_values(by=["Date"])

    # Cash On Hand
df_BalanceSheet["Cash On Hand"] = df_BalanceSheet["Cash On Hand"].replace("",0)
df_BalanceSheet["Cash On Hand"] = df_BalanceSheet["Cash On Hand"].astype("float64")
df_BalanceSheet["Cash On Hand"] = df_BalanceSheet["Cash On Hand"] * 1000000
df_BalanceSheet["Cash On Hand - QoQ"] = df_BalanceSheet["Cash On Hand"].pct_change(1).replace([np.inf,-np.inf],0)
df_BalanceSheet["Cash On Hand - YoY"] = df_BalanceSheet["Cash On Hand"].pct_change(4).replace([np.inf,-np.inf],0)
df_BalanceSheet["Cash On Hand - 5Y CAGR"]  = ((df_BalanceSheet['Cash On Hand'].pct_change(20)+1)**0.2)-1   
df_BalanceSheet["Cash On Hand - 5Y CAGR"] = df_BalanceSheet["Cash On Hand - 5Y CAGR"].replace([np.inf,-np.inf],0)

    # Total Current Assets
df_BalanceSheet["Total Current Assets"] = df_BalanceSheet["Total Current Assets"].replace("",0)
df_BalanceSheet["Total Current Assets"] = df_BalanceSheet["Total Current Assets"].astype("float64")
df_BalanceSheet["Total Current Assets"] = df_BalanceSheet["Total Current Assets"] * 1000000
df_BalanceSheet["Total Current Assets - QoQ"] = df_BalanceSheet["Total Current Assets"].pct_change(1).replace([np.inf,-np.inf],0)
df_BalanceSheet["Total Current Assets - YoY"] = df_BalanceSheet["Total Current Assets"].pct_change(4).replace([np.inf,-np.inf],0)
df_BalanceSheet["Total Current Assets - 5Y CAGR"]  = ((df_BalanceSheet['Total Current Assets'].pct_change(20)+1)**0.2)-1    
df_BalanceSheet["Total Current Assets - 5Y CAGR"] = df_BalanceSheet["Total Current Assets - 5Y CAGR"].replace([np.inf,-np.inf],0)
    
    # Total Current Liabilities
df_BalanceSheet["Total Current Liabilities"] = df_BalanceSheet["Total Current Liabilities"].replace("",0)
df_BalanceSheet["Total Current Liabilities"] = df_BalanceSheet["Total Current Liabilities"].astype("float64") *-1
df_BalanceSheet["Total Current Liabilities"] = df_BalanceSheet["Total Current Liabilities"] * 1000000
df_BalanceSheet["Total Current Liabilities - QoQ"] = df_BalanceSheet["Total Current Liabilities"].pct_change(1).replace([np.inf,-np.inf],0)
df_BalanceSheet["Total Current Liabilities - YoY"] = df_BalanceSheet["Total Current Liabilities"].pct_change(4).replace([np.inf,-np.inf],0)
df_BalanceSheet["Total Current Liabilities - 5Y CAGR"]  = ((df_BalanceSheet['Total Current Liabilities'].pct_change(20)+1)**0.2)-1    
df_BalanceSheet["Total Current Liabilities - 5Y CAGR"] = df_BalanceSheet["Total Current Liabilities - 5Y CAGR"].replace([np.inf,-np.inf],0)
  
    # Total Liabilities
df_BalanceSheet["Total Liabilities"] = df_BalanceSheet["Total Liabilities"].replace("",0)
df_BalanceSheet["Total Liabilities"] = df_BalanceSheet["Total Liabilities"].astype("float64") *-1
df_BalanceSheet["Total Liabilities"] = df_BalanceSheet["Total Liabilities"] * 1000000
df_BalanceSheet["Total Liabilities - QoQ"] = df_BalanceSheet["Total Liabilities"].pct_change(1).replace([np.inf,-np.inf],0)
df_BalanceSheet["Total Liabilities - YoY"] = df_BalanceSheet["Total Liabilities"].pct_change(4).replace([np.inf,-np.inf],0)
df_BalanceSheet["Total Liabilities - 5Y CAGR"]  = ((df_BalanceSheet['Total Liabilities'].pct_change(20)+1)**0.2)-1    
df_BalanceSheet["Total Liabilities - 5Y CAGR"] = df_BalanceSheet["Total Liabilities - 5Y CAGR"].replace([np.inf,-np.inf],0)

    
    # Shareholder Equity
df_BalanceSheet["Share Holder Equity"] = df_BalanceSheet["Share Holder Equity"].replace("",0)
df_BalanceSheet["Share Holder Equity"] = df_BalanceSheet["Share Holder Equity"].astype("float64")
df_BalanceSheet["Share Holder Equity"] = df_BalanceSheet["Share Holder Equity"] * 1000000
df_BalanceSheet["Share Holder Equity - QoQ"] = df_BalanceSheet["Share Holder Equity"].pct_change(1).replace([np.inf,-np.inf],0)
df_BalanceSheet["Share Holder Equity - YoY"] = df_BalanceSheet["Share Holder Equity"].pct_change(4).replace([np.inf,-np.inf],0)
df_BalanceSheet["Share Holder Equity - 5Y CAGR"]  = ((df_BalanceSheet['Share Holder Equity'].pct_change(20)+1)**0.2)-1    
df_BalanceSheet["Share Holder Equity - 5Y CAGR"] = df_BalanceSheet["Share Holder Equity - 5Y CAGR"].replace([np.inf,-np.inf],0)


    # Shareholder Equity
df_BalanceSheet["Long Term Debt"] = df_BalanceSheet["Long Term Debt"].replace("",0).replace([np.inf,-np.inf],0).replace("inf",0)
df_BalanceSheet["Long Term Debt"] = df_BalanceSheet["Long Term Debt"].astype("float64") *-1
df_BalanceSheet["Long Term Debt"] = df_BalanceSheet["Long Term Debt"] * 1000000
df_BalanceSheet["Long Term Debt - QoQ"] = df_BalanceSheet["Long Term Debt"].pct_change(1).replace([np.inf,-np.inf],0)
df_BalanceSheet["Long Term Debt - YoY"] = df_BalanceSheet["Long Term Debt"].pct_change(4).replace([np.inf,-np.inf],0)
df_BalanceSheet["Long Term Debt - 5Y CAGR"]  = ((df_BalanceSheet['Long Term Debt'].pct_change(20)+1)**0.2)-1
df_BalanceSheet["Long Term Debt - 5Y CAGR"] = df_BalanceSheet["Long Term Debt - 5Y CAGR"].replace([np.inf,-np.inf],0)

#%% Cash Flow Statement
html = requests.get(cashflowstatement)
soup = BeautifulSoup(html.text, 'html.parser')
htmltext = soup.prettify()

varlist = {}
vars  = htmltext.split("var ")[1:]  # get each var entry
for v in vars:
    name = v.split("=")[0].strip()  # first part is the var [name = "]
    try:
        value = v.split("originalData = ")[1]        # second part is the value [ = "..."]
        value = value.replace(";","")
    except:
        value = 0
    varlist[name] = value           # store it for printing below           

originalData = varlist["originalData"]

data = json.loads(originalData)
df_CashFlowStatement = pd.DataFrame.from_dict(data)
df_CashFlowStatement["field_name"] = df_CashFlowStatement["field_name"].str.split(">").str[1]
df_CashFlowStatement["field_name"] = df_CashFlowStatement["field_name"].str.split("<").str[0]
df_CashFlowStatement = df_CashFlowStatement.drop(["popup_icon"], axis = 1)
df_CashFlowStatement = df_CashFlowStatement.rename(columns = {'field_name':'Date'})
df_CashFlowStatement.index = df_CashFlowStatement["Date"]
df_CashFlowStatement = df_CashFlowStatement.drop(["Date"], axis = 1)
df_CashFlowStatement = df_CashFlowStatement.T
df_CashFlowStatement = df_CashFlowStatement.reset_index()
df_CashFlowStatement = df_CashFlowStatement.rename(columns = {'index':'Date'})

# Calculated Values
df_CashFlowStatement = df_CashFlowStatement.sort_values(by=["Date"])

    # Cash Flow From Operating Activities
df_CashFlowStatement["Cash Flow From Operating Activities"] = df_CashFlowStatement["Cash Flow From Operating Activities"].replace("",0)
df_CashFlowStatement["Operating Cash Flow"] = df_CashFlowStatement["Cash Flow From Operating Activities"].astype("float64")
df_CashFlowStatement["Operating Cash Flow"] = df_CashFlowStatement["Operating Cash Flow"] * 1000000
df_CashFlowStatement["Operating Cash Flow - QoQ"] = df_CashFlowStatement["Operating Cash Flow"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Operating Cash Flow - YoY"] = df_CashFlowStatement["Operating Cash Flow"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Operating Cash Flow TTM"] = df_CashFlowStatement["Operating Cash Flow"].rolling(4).sum() 
df_CashFlowStatement["Operating Cash Flow TTM - QoQ"] = df_CashFlowStatement["Operating Cash Flow TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Operating Cash Flow TTM - YoY"] = df_CashFlowStatement["Operating Cash Flow TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Operating Cash Flow TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Operating Cash Flow TTM'].pct_change(20)+1)**0.2)-1    
df_CashFlowStatement["Operating Cash Flow TTM - 5Y CAGR"] = df_CashFlowStatement["Operating Cash Flow TTM - 5Y CAGR"].replace([np.inf,-np.inf],0) 
    
    # Cash Flow From Investing Activities
df_CashFlowStatement["Cash Flow From Investing Activities"] = df_CashFlowStatement["Cash Flow From Investing Activities"].replace("",0)
df_CashFlowStatement["Investing Cash Flow"] = df_CashFlowStatement["Cash Flow From Investing Activities"].astype("float64")
df_CashFlowStatement["Investing Cash Flow"] = df_CashFlowStatement["Investing Cash Flow"] * 1000000
df_CashFlowStatement["Investing Cash Flow - QoQ"] = df_CashFlowStatement["Investing Cash Flow"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Investing Cash Flow - YoY"] = df_CashFlowStatement["Investing Cash Flow"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Investing Cash Flow TTM"] = df_CashFlowStatement["Investing Cash Flow"].rolling(4).sum() 
df_CashFlowStatement["Investing Cash Flow TTM - QoQ"] = df_CashFlowStatement["Investing Cash Flow TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Investing Cash Flow TTM - YoY"] = df_CashFlowStatement["Investing Cash Flow TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Investing Cash Flow TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Investing Cash Flow TTM'].pct_change(20)+1)**0.2)-1        
df_CashFlowStatement["Investing Cash Flow TTM - 5Y CAGR"] = df_CashFlowStatement["Investing Cash Flow TTM - 5Y CAGR"].replace([np.inf,-np.inf],0) 
    
    # Cash Flow From Financing Activities
df_CashFlowStatement["Cash Flow From Financial Activities"] = df_CashFlowStatement["Cash Flow From Financial Activities"].replace("",0)
df_CashFlowStatement["Financing Cash Flow"] = df_CashFlowStatement["Cash Flow From Financial Activities"].astype("float64")
df_CashFlowStatement["Financing Cash Flow"] = df_CashFlowStatement["Financing Cash Flow"] * 1000000
df_CashFlowStatement["Financing Cash Flow - QoQ"] = df_CashFlowStatement["Financing Cash Flow"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Financing Cash Flow - YoY"] = df_CashFlowStatement["Financing Cash Flow"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Financing Cash Flow TTM"] = df_CashFlowStatement["Financing Cash Flow"].rolling(4).sum() 
df_CashFlowStatement["Financing Cash Flow TTM - QoQ"] = df_CashFlowStatement["Financing Cash Flow TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Financing Cash Flow TTM - YoY"] = df_CashFlowStatement["Financing Cash Flow TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Financing Cash Flow TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Financing Cash Flow TTM'].pct_change(20)+1)**0.2)-1            
df_CashFlowStatement["Financing Cash Flow TTM - 5Y CAGR"] = df_CashFlowStatement["Financing Cash Flow TTM - 5Y CAGR"].replace([np.inf,-np.inf],0) 
    
    #  Net Cash Flow
df_CashFlowStatement["Net Cash Flow"] = df_CashFlowStatement["Net Cash Flow"].replace("",0)
df_CashFlowStatement["Net Cash Flow"] = df_CashFlowStatement["Net Cash Flow"].astype("float64")
df_CashFlowStatement["Net Cash Flow"] = df_CashFlowStatement["Net Cash Flow"] * 1000000
df_CashFlowStatement["Net Cash Flow - QoQ"] = df_CashFlowStatement["Net Cash Flow"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Net Cash Flow - YoY"] = df_CashFlowStatement["Net Cash Flow"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Net Cash Flow TTM"] = df_CashFlowStatement["Net Cash Flow"].rolling(4).sum() 
df_CashFlowStatement["Net Cash Flow TTM - QoQ"] = df_CashFlowStatement["Net Cash Flow TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Net Cash Flow TTM - YoY"] = df_CashFlowStatement["Net Cash Flow TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Net Cash Flow TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Net Cash Flow TTM'].pct_change(20)+1)**0.2)-1         
df_CashFlowStatement["Net Cash Flow TTM - 5Y CAGR"] = df_CashFlowStatement["Net Cash Flow TTM - 5Y CAGR"].replace([np.inf,-np.inf],0) 
   
    # Stock-Based Compensation
df_CashFlowStatement["Stock-Based Compensation"] = df_CashFlowStatement["Stock-Based Compensation"].replace("",0)
df_CashFlowStatement["Stock-Based Compensation"] = df_CashFlowStatement["Stock-Based Compensation"].astype("float64")
df_CashFlowStatement["Stock-Based Compensation"] = df_CashFlowStatement["Stock-Based Compensation"] * 1000000
df_CashFlowStatement["Stock-Based Compensation - QoQ"] = df_CashFlowStatement["Stock-Based Compensation"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Stock-Based Compensation - YoY"] = df_CashFlowStatement["Stock-Based Compensation"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Stock-Based Compensation TTM"] = df_CashFlowStatement["Stock-Based Compensation"].rolling(4).sum() 
df_CashFlowStatement["Stock-Based Compensation TTM - QoQ"] = df_CashFlowStatement["Stock-Based Compensation TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Stock-Based Compensation TTM - YoY"] = df_CashFlowStatement["Stock-Based Compensation TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Stock-Based Compensation TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Stock-Based Compensation TTM'].pct_change(20)+1)**0.2)-1        
df_CashFlowStatement["Stock-Based Compensation TTM - 5Y CAGR"] = df_CashFlowStatement["Stock-Based Compensation TTM - 5Y CAGR"].replace([np.inf,-np.inf],0) 
      
    # Common Stock Dividends Paid
df_CashFlowStatement["Common Stock Dividends Paid"] = df_CashFlowStatement["Common Stock Dividends Paid"].replace("",0)
df_CashFlowStatement["Common Stock Dividends Paid"] = df_CashFlowStatement["Common Stock Dividends Paid"].astype("float64")
df_CashFlowStatement["Common Stock Dividends Paid"] = df_CashFlowStatement["Common Stock Dividends Paid"] * 1000000
df_CashFlowStatement["Common Stock Dividends Paid - QoQ"] = df_CashFlowStatement["Common Stock Dividends Paid"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Common Stock Dividends Paid - YoY"] = df_CashFlowStatement["Common Stock Dividends Paid"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Common Stock Dividends Paid TTM"] = df_CashFlowStatement["Common Stock Dividends Paid"].rolling(4).sum() 
df_CashFlowStatement["Common Stock Dividends Paid TTM - QoQ"] = df_CashFlowStatement["Common Stock Dividends Paid TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Common Stock Dividends Paid TTM - YoY"] = df_CashFlowStatement["Common Stock Dividends Paid TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Common Stock Dividends Paid TTM - 5Y CAGR"] = ((df_CashFlowStatement['Common Stock Dividends Paid TTM'].pct_change(20)+1)**0.2)-1     
df_CashFlowStatement["Common Stock Dividends Paid TTM - 5Y CAGR"] = df_CashFlowStatement["Common Stock Dividends Paid TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)    

    # Share Buybacks
df_CashFlowStatement["Share Buybacks"] = df_CashFlowStatement["Net Common Equity Issued/Repurchased"].replace("",0)
df_CashFlowStatement["Share Buybacks"] = df_CashFlowStatement["Share Buybacks"].astype("float64")
df_CashFlowStatement["Share Buybacks"] = df_CashFlowStatement["Share Buybacks"] * 1000000
df_CashFlowStatement["Share Buybacks - QoQ"] = df_CashFlowStatement["Share Buybacks"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Share Buybacks - YoY"] = df_CashFlowStatement["Share Buybacks"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Share Buybacks TTM"] = df_CashFlowStatement["Share Buybacks"].rolling(4).sum() 
df_CashFlowStatement["Share Buybacks TTM - QoQ"] = df_CashFlowStatement["Share Buybacks TTM"].pct_change(1).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Share Buybacks TTM - YoY"] = df_CashFlowStatement["Share Buybacks TTM"].pct_change(4).replace([np.inf,-np.inf],0)
df_CashFlowStatement["Share Buybacks TTM - 5Y CAGR"] = ((df_CashFlowStatement['Share Buybacks TTM'].pct_change(20)+1)**0.2)-1     
df_CashFlowStatement["Share Buybacks TTM - 5Y CAGR"] = df_CashFlowStatement["Share Buybacks TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)        
      
#%% Data Ingestions


Q_Fcf       = pd.read_html(fcf)[1] 
# Q_OpEx      = pd.read_html(opex)[1]
Q_RnD       = pd.read_html(rnd)[1]


# Quarterly Data (Rates where only Q are available)
  # 0 for Quarterly Data, 1 for Company Metadata
Q_Roe       = pd.read_html(roe)[0]
Q_Roi       = pd.read_html(roi)[0] 
Q_Roa       = pd.read_html(roa)[0] 
Q_GrossM    = pd.read_html(grossmarg)[0] 
Q_OperatingM = pd.read_html(opermarg)[0] 

# FCF & TTM FCF
Q_Fcf.columns = ['Date','FCF'] # Rename cols
Q_Fcf["Date"] = pd.to_datetime(Q_Fcf["Date"]) # converts date to datetime from object
Q_Fcf["FCF"] = pd.to_numeric(Q_Fcf["FCF"]) # converts FCF to float from object
Q_Fcf.sort_values("Date", inplace=True) # Sort dates by ascending
Q_Fcf["TTM FCF"] = Q_Fcf["FCF"].rolling(4).sum() # Creates trailing 12 month sum

# FCF Pct Changes
Q_Fcf["FCF QoQ"] = Q_Fcf['FCF'].pct_change(1)
Q_Fcf["FCF YoY"] = Q_Fcf['FCF'].pct_change(4)

# TTM FCF Pct Changes
Q_Fcf["TTM FCF QoQ"] = Q_Fcf['TTM FCF'].pct_change(1)
Q_Fcf["TTM FCF YoY"] = Q_Fcf['TTM FCF'].pct_change(4)
Q_Fcf["TTM FCF 5Y CAGR"]  = ((Q_Fcf['TTM FCF'].pct_change(20)+1)**0.2)-1
Q_Fcf = Q_Fcf[Q_Fcf["Date"]>start_date] # Snips data to target time frame

# ROE
Q_Roe.columns = ['Date','drop_1','drop_2','ROE'] # Rename cols
Q_Roe = Q_Roe[['Date','ROE']]
Q_Roe["ROE"] = Q_Roe["ROE"].str.replace("[%]","",regex=True) # Removes commas and $ from FCF
Q_Roe["Date"] = pd.to_datetime(Q_Roe["Date"]) # converts date to datetime from object
Q_Roe["ROE"] = pd.to_numeric(Q_Roe["ROE"]) # converts FCF to float from object
Q_Roe["ROE"] = Q_Roe["ROE"]/100 # turn % to fraction
Q_Roe.sort_values("Date", inplace=True) # Sort dates by ascending

# ROE Pct Changes
Q_Roe["ROE QoQ"] = Q_Roe['ROE'].pct_change(1)
Q_Roe["ROE YoY"] = Q_Roe['ROE'].pct_change(4)
Q_Roe["ROE 5Y CAGR"]  = ((Q_Roe['ROE'].pct_change(20)+1)**0.2)-1


#ROI
Q_Roi.columns = ['Date','drop_1','drop_2','ROI'] # Rename cols
Q_Roi=Q_Roi.dropna()
Q_Roi = Q_Roi[['Date','ROI']]
Q_Roi["ROI"] = Q_Roi["ROI"].str.replace("[%]","",regex=True) # Removes commas and $ from FCF
Q_Roi["Date"] = pd.to_datetime(Q_Roi["Date"]) # converts date to datetime from object
Q_Roi["ROI"] = pd.to_numeric(Q_Roi["ROI"]) # converts FCF to float from object
Q_Roi["ROI"] = Q_Roi["ROI"]/100 # turn % to fraction
Q_Roi.sort_values("Date", inplace=True) # Sort dates by ascending

# ROI Pct Changes
Q_Roi["ROI QoQ"] = Q_Roi['ROI'].pct_change(1)
Q_Roi["ROI YoY"] = Q_Roi['ROI'].pct_change(4)
Q_Roi["ROI 5Y CAGR"]  = ((Q_Roi['ROI'].pct_change(20)+1)**0.2)-1


#ROA
Q_Roa.columns = ['Date','drop_1','drop_2','ROA'] # Rename cols
Q_Roa = Q_Roa[['Date','ROA']]
Q_Roa["ROA"] = Q_Roa["ROA"].str.replace("[%]","",regex=True) # Removes commas and $ from FCF
Q_Roa["Date"] = pd.to_datetime(Q_Roa["Date"]) # converts date to datetime from object
Q_Roa["ROA"] = pd.to_numeric(Q_Roa["ROA"]) # converts FCF to float from object
Q_Roa["ROA"] = Q_Roa["ROA"]/100 # turn % to fraction
Q_Roa.sort_values("Date", inplace=True) # Sort dates by ascending

# ROA Pct Changes
Q_Roa["ROA QoQ"] = Q_Roa['ROA'].pct_change(1)
Q_Roa["ROA YoY"] = Q_Roa['ROA'].pct_change(4)
Q_Roa["ROA 5Y CAGR"]  = ((Q_Roa['ROA'].pct_change(20)+1)**0.2)-1

Q_Roa = Q_Roa[Q_Roa["Date"]>start_date] # Snips data to target time frame
Q_Roe = Q_Roe[Q_Roe["Date"]>start_date] # Snips data to target time frame
Q_Roi = Q_Roi[Q_Roi["Date"]>start_date] # Snips data to target time frame


# Gross Margin
Q_GrossM.columns = ['Date','drop_1','drop_2','Gross Margin'] # Rename cols
Q_GrossM = Q_GrossM[['Date','Gross Margin']]
Q_GrossM["Gross Margin"] = Q_GrossM["Gross Margin"].str.replace("[%]","",regex=True) # Removes commas and $ from Gross Margin
Q_GrossM["Date"] = pd.to_datetime(Q_GrossM["Date"]) # converts date to datetime from object
Q_GrossM["Gross Margin"] = pd.to_numeric(Q_GrossM["Gross Margin"]) # converts Gross Margin to float from object
Q_GrossM["Gross Margin"] = Q_GrossM["Gross Margin"]/100 # turn % to fraction
Q_GrossM.sort_values("Date", inplace=True) # Sort dates by ascending

# Gross Margin Pct Changes
Q_GrossM["Gross Margin QoQ"] = Q_GrossM['Gross Margin'].pct_change(1)
Q_GrossM["Gross Margin YoY"] = Q_GrossM['Gross Margin'].pct_change(4)
Q_GrossM["Gross Margin 5Y CAGR"]  = ((Q_GrossM['Gross Margin'].pct_change(20)+1)**0.2)-1

# Operating Margin
Q_OperatingM.columns = ['Date','drop_1','drop_2','Operating Margin'] # Rename cols
Q_OperatingM = Q_OperatingM[['Date','Operating Margin']]
Q_OperatingM["Operating Margin"] = Q_OperatingM["Operating Margin"].str.replace("[%]","",regex=True) # Removes commas and $ from Gross Margin
Q_OperatingM["Date"] = pd.to_datetime(Q_OperatingM["Date"]) # converts date to datetime from object
Q_OperatingM["Operating Margin"] = pd.to_numeric(Q_OperatingM["Operating Margin"]) # converts Operating Margin to float from object
Q_OperatingM["Operating Margin"] = Q_OperatingM["Operating Margin"]/100 # turn % to fraction
Q_OperatingM.sort_values("Date", inplace=True) # Sort dates by ascending

# Operating Margin Pct Changes
Q_OperatingM["Operating Margin QoQ"] = Q_OperatingM['Operating Margin'].pct_change(1)
Q_OperatingM["Operating Margin YoY"] = Q_OperatingM['Operating Margin'].pct_change(4)
Q_OperatingM["Operating Margin 5Y CAGR"]  = ((Q_OperatingM['Operating Margin'].pct_change(20)+1)**0.2)-1


# Net Margin
Q_NetM = pd.read_html(netmarg)[0] # 0 for Annual, 1 for Quarterly #! REMOVE WHEN FINISHED
Q_NetM.columns = ['Date','drop_1','drop_2','Net Margin'] # Rename cols
Q_NetM = Q_NetM[['Date','Net Margin']]
Q_NetM["Net Margin"] = Q_NetM["Net Margin"].str.replace("[%]","",regex=True) # Removes commas and $ from Gross Margin
Q_NetM["Date"] = pd.to_datetime(Q_NetM["Date"]) # converts date to datetime from object
Q_NetM["Net Margin"] = pd.to_numeric(Q_NetM["Net Margin"]) # converts Operating Margin to float from object
Q_NetM["Net Margin"] = Q_NetM["Net Margin"]/100 # turn % to fraction
Q_NetM.sort_values("Date", inplace=True) # Sort dates by ascending

# Net Margin Pct Changes
Q_NetM["Net Margin QoQ"] = Q_NetM['Net Margin'].pct_change(1)
Q_NetM["Net Margin YoY"] = Q_NetM['Net Margin'].pct_change(4)
Q_NetM["Net Margin 5Y CAGR"]  = ((Q_NetM['Net Margin'].pct_change(20)+1)**0.2)-1

Q_GrossM = Q_GrossM[Q_GrossM["Date"]>start_date] # Snips data to target time frame
Q_OperatingM = Q_OperatingM[Q_OperatingM["Date"]>start_date] # Snips data to target time frame
Q_NetM = Q_NetM[Q_NetM["Date"]>start_date] # Snips data to target time frame

# R&D & TTM R&D
Q_RnD.columns = ['Date','R&D'] # Rename cols
if 1==1:
  try:
    Q_RnD["R&D"] = Q_RnD["R&D"].str.replace("[$,]","",regex=True) # Removes commas and $ from EPS
  except:
    pass
Q_RnD["Date"] = pd.to_datetime(Q_RnD["Date"]) # converts date to datetime from object
Q_RnD["R&D"] = pd.to_numeric(Q_RnD["R&D"]) # converts EPS to float from object

Q_RnD.sort_values("Date", inplace=True) # Sort dates by ascending
Q_RnD["TTM R&D"] = Q_RnD["R&D"].rolling(4).sum() # Creates trailing 12 month sum

# R&D Pct Changes
Q_RnD["R&D QoQ"] = Q_RnD['R&D'].pct_change(1)
Q_RnD["R&D YoY"] = Q_RnD['R&D'].pct_change(4)

# TTM R&D Pct Changes
Q_RnD["TTM R&D QoQ"] = Q_RnD['TTM R&D'].pct_change(1)
Q_RnD["TTM R&D YoY"] = Q_RnD['TTM R&D'].pct_change(4)
Q_RnD["TTM R&D 5Y CAGR"]  = ((Q_RnD['TTM R&D'].pct_change(20)+1)**0.2)-1

#Q_OpEx = Q_OpEx[Q_OpEx["Date"]>start_date] # Snips data to target time frame
Q_RnD = Q_RnD[Q_RnD["Date"]>start_date] # Snips data to target time frame

#%% Price Data

stock = yf.Ticker(ticker)
stock_all = stock.history(period="max")
df_histprice = stock_all[["Close"]]

# SMA
df_histprice["50d SMA"] = df_histprice["Close"].rolling(window = 50).mean()
df_histprice["250d SMA"] = df_histprice["Close"].rolling(window = 250).mean()
df_histprice["Date"] = df_histprice.index
df_histprice = df_histprice[df_histprice.index>=start_date]
df_histprice_cols = df_histprice.columns.tolist()
df_histprice_cols = df_histprice_cols[-1:] + df_histprice_cols[:-1]
df_histprice = df_histprice[df_histprice_cols]
df_dates = pd.DataFrame({'Date':pd.date_range(start=start_date, end=datetime.today())})
df_histprice = df_histprice.reset_index(drop=True)
df_histprice['Date'] = df_histprice['Date'].dt.tz_localize(None)
df_price = pd.merge(df_dates, df_histprice, how = 'left', left_on='Date', right_on = 'Date')
df_price = df_price.ffill(axis=0)

#%%
# P/E With Quantiles
df_eps = df_IncomeStatement[["Date","EPS TTM"]]
df_eps = df_eps.astype({"Date": 'datetime64[ns]'})
df_price = df_histprice.merge(df_eps, how = "left", left_on = "Date", right_on = "Date")
df_price = df_price.ffill(axis=0)
df_price["P/E"] = df_price["Close"]/df_price["EPS TTM"]
df_price.loc[df_price["P/E"] < 0, "P/E"] = 0
df_price["P/E Lower Quintile"] = df_price["P/E"].rolling(1460).quantile(.2)
df_price["P/E Upper Quintile"] = df_price["P/E"].rolling(1460).quantile(.8)

# P/S With Quantiles
df_shares = df_IncomeStatement[["Date","Shares Outstanding","Revenue TTM"]]
df_shares = df_shares.astype({"Date": 'datetime64[ns]'})
df_price = df_price.merge(df_shares, how="left", left_on = "Date", right_on = "Date")
df_price = df_price.ffill(axis=0)
df_price["MCap"] = df_price["Close"]*df_price["Shares Outstanding"]
df_price["P/S"] =  df_price["MCap"]/df_price["Revenue TTM"]
df_price["P/S Lower Quintile"] = df_price["P/S"].rolling(1460).quantile(.2)
df_price["P/S Upper Quintile"] = df_price["P/S"].rolling(1460).quantile(.8)

#%%

pd.set_option('display.max_colwidth', 25)

# Set up scraper
req = Request(fv, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
html = BeautifulSoup(webpage, "html.parser")

try:
    # Find fundamentals table
    fundamentals = pd.read_html(str(html), attrs = {'class': 'snapshot-table2'})[0]
    
    # Clean up fundamentals dataframe
    fundamentals.columns = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    colOne = []
    colLength = len(fundamentals)
    for k in np.arange(0, colLength, 2):
        colOne.append(fundamentals[f'{k}'])
    attrs = pd.concat(colOne, ignore_index=True)
    
    colTwo = []
    colLength = len(fundamentals)
    for k in np.arange(1, colLength, 2):
        colTwo.append(fundamentals[f'{k}'])
    vals = pd.concat(colTwo, ignore_index=True)
    
    fundamentals = pd.DataFrame()
    fundamentals['Attributes'] = attrs
    fundamentals['Values'] = vals
    fundamentals = fundamentals.set_index('Attributes')
    

except Exception as e:
    e

# Fix missing values
df_fundamentals = fundamentals.T
df_fundamentals["ticker"] = ticker
df_fundamentals["company"] = company
df_fundamentals["company_b"] = company_beaut
df_fundamentals["version_name"] = version_name
df_fundamentals["version_number"] = "version "+version_number

for (columnName, columnData) in df_fundamentals.iteritems():
    df_fundamentals[columnName] = np.where(df_fundamentals[columnName] == "-", 0, df_fundamentals[columnName])
    
#%% Merge 

# Merge Quarterly Data
df_data = Q_Fcf.merge(Q_Roe, how="left", left_on='Date', right_on='Date')
df_data = df_data.merge(Q_Roa, left_on = 'Date', right_on = 'Date')

if len(Q_Roi) > 0:
  df_data = df_data.merge(Q_Roi, how="left", left_on = 'Date', right_on = 'Date')
else:
  df_data["ROI"] = ""
  df_data["ROI QoQ"] = ""
  df_data["ROI YoY"]  = ""
  df_data["ROI 5Y CAGR"] = ""
  
df_data = df_data.merge(Q_GrossM, left_on = 'Date', right_on = 'Date')
df_data = df_data.merge(Q_OperatingM, left_on = 'Date', right_on = 'Date')
df_data = df_data.merge(Q_NetM, left_on = 'Date', right_on = 'Date')
df_data = df_data.merge(Q_RnD, left_on = 'Date', right_on = 'Date')


df_data = df_data.sort_values(by=['Date'], ascending = False)
df_data = df_data.reset_index()
df_data = df_data.drop("index", axis=1)


#%%

# To Excel
with pd.ExcelWriter('C:/Users/eirik/OneDrive/Documents/Cloudkit/PowerBI Resources/BDR.xlsx') as writer:  
    df_data.to_excel(writer, sheet_name='Quarterly Data')
    df_price.to_excel(writer, sheet_name='Price Data')
    df_fundamentals.to_excel(writer, sheet_name='Info') 
    df_IncomeStatement.to_excel(writer, sheet_name='Income Statement', index = False) 
    df_BalanceSheet.to_excel(writer, sheet_name='Balance Sheet', index = False) 
    df_CashFlowStatement.to_excel(writer, sheet_name='Cash Flow Statement', index = False) 

    
# End Execution
print("Execution time:  %s seconds" % round((time.time() - start_time),2))
