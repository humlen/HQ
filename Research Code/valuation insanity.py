# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 14:48:24 2023

@author: eirik
"""

import yfinance as yf
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import numpy as np
from bs4 import BeautifulSoup 
import requests
import json
import time

tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__tickers.csv")
start_date = '2010-01-01'

tickerlist = tickers["ticker"].tolist()[2750:]
companylist = tickers["comp_name"].tolist()[2750:]


# Resources
mt =                "https://www.macrotrends.net/stocks/charts/"

#%%
dflist = []


for i in tqdm(range(len(tickerlist))):
    ticker = tickerlist[i]
    company = companylist[i]
    stock = yf.Ticker(ticker)
    stock_all = stock.history(period="max")
    df_histprice = stock_all[["Close"]]
    incomestatement =   "{base}{ticker}/{company}/income-statement?freq=Q".format(ticker=ticker,company=company,base=mt)
    cashflowstatement = "{base}{ticker}/{company}/cash-flow-statement?freq=Q".format(ticker=ticker,company=company,base=mt)

    try:
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
        df_CashFlowStatement["Operating Cash Flow"] = df_CashFlowStatement["Operating Cash Flow"] * 1_000_000
        df_CashFlowStatement["Operating Cash Flow - QoQ"] = df_CashFlowStatement["Operating Cash Flow"].pct_change(1).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Operating Cash Flow - YoY"] = df_CashFlowStatement["Operating Cash Flow"].pct_change(4).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Operating Cash Flow TTM"] = df_CashFlowStatement["Operating Cash Flow"].rolling(4).sum() 
        df_CashFlowStatement["Operating Cash Flow TTM - QoQ"] = df_CashFlowStatement["Operating Cash Flow TTM"].pct_change(1).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Operating Cash Flow TTM - YoY"] = df_CashFlowStatement["Operating Cash Flow TTM"].pct_change(4).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Operating Cash Flow TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Operating Cash Flow TTM'].pct_change(20)+1)**0.2)-1    
        df_CashFlowStatement["Operating Cash Flow TTM - 5Y CAGR"] = df_CashFlowStatement["Operating Cash Flow TTM - 5Y CAGR"].replace([np.inf,-np.inf],0) 
    
            # Capital Expenditure
        df_CashFlowStatement["Capital Expenditure"] = df_CashFlowStatement["Total Depreciation And Amortization - Cash Flow"].replace("",0).astype("float64") + df_CashFlowStatement["Net Change In Property, Plant, And Equipment"].replace("",0).astype("float64") 
        df_CashFlowStatement["Capital Expenditure"] = df_CashFlowStatement["Capital Expenditure"] * 1_000_000
        df_CashFlowStatement["Capital Expenditure - QoQ"] = df_CashFlowStatement["Capital Expenditure"].pct_change(1).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Capital Expenditure - YoY"] = df_CashFlowStatement["Capital Expenditure"].pct_change(4).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Capital Expenditure TTM"] = df_CashFlowStatement["Capital Expenditure"].rolling(4).sum() 
        df_CashFlowStatement["Capital Expenditure TTM - QoQ"] = df_CashFlowStatement["Capital Expenditure TTM"].pct_change(1).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Capital Expenditure TTM - YoY"] = df_CashFlowStatement["Capital Expenditure TTM"].pct_change(4).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Capital Expenditure TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Capital Expenditure TTM'].pct_change(20)+1)**0.2)-1         
        df_CashFlowStatement["Capital Expenditure TTM - 5Y CAGR"] = df_CashFlowStatement["Capital Expenditure TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)
        
            # Free Cash Flow
        df_CashFlowStatement["Free Cash Flow"] = df_CashFlowStatement["Operating Cash Flow"] - df_CashFlowStatement["Capital Expenditure"]
        df_CashFlowStatement["Free Cash Flow - QoQ"] = df_CashFlowStatement["Free Cash Flow"].pct_change(1).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Free Cash Flow - YoY"] = df_CashFlowStatement["Free Cash Flow"].pct_change(4).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Free Cash Flow TTM"] = df_CashFlowStatement["Free Cash Flow"].rolling(4).sum() 
        df_CashFlowStatement["Free Cash Flow TTM - QoQ"] = df_CashFlowStatement["Free Cash Flow TTM"].pct_change(1).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Free Cash Flow TTM - YoY"] = df_CashFlowStatement["Free Cash Flow TTM"].pct_change(4).replace([np.inf,-np.inf],0)
        df_CashFlowStatement["Free Cash Flow TTM - 5Y CAGR"]  = ((df_CashFlowStatement['Free Cash Flow TTM'].pct_change(20)+1)**0.2)-1         
        df_CashFlowStatement["Free Cash Flow TTM - 5Y CAGR"] = df_CashFlowStatement["Free Cash Flow TTM - 5Y CAGR"].replace([np.inf,-np.inf],0)   
        
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
        df_price_raw = pd.merge(df_dates, df_histprice, how = 'left', left_on='Date', right_on = 'Date')
        df_price_raw = df_price_raw.ffill(axis=0)
        
        
        # Revenue / MCap 
        df_shares = df_IncomeStatement[["Date","Shares Outstanding","Revenue TTM"]]
        df_shares = df_shares.astype({"Date": 'datetime64[ns]'})
        df_price = df_price_raw.merge(df_shares, how="left", left_on = "Date", right_on = "Date")
        df_price = df_price.ffill(axis=0)
        df_price["Market Capitalization"] = df_price["Close"]*df_price["Shares Outstanding"]
        df_price = df_price.dropna()
        df_price["Revenue / Market Capitalization"] = df_price["Revenue TTM"] / df_price["Market Capitalization"] * 100
        df_price["Revenue / Market Capitalization Lower Quintile"] = df_price["Revenue / Market Capitalization"].rolling(1460).quantile(.15, interpolation = 'midpoint')
        df_price["Revenue / Market Capitalization Upper Quintile"] = df_price["Revenue / Market Capitalization"].rolling(1460).quantile(.85, interpolation = 'midpoint') 
    
        # EBITDA / MCap With Quantiles
        df_ebidta = df_IncomeStatement[["Date","EBITDA TTM"]]
        df_ebidta = df_ebidta.astype({"Date": 'datetime64[ns]'})
        df_price = df_price.merge(df_ebidta, how = "left", left_on = "Date", right_on = "Date")
        df_price = df_price.ffill(axis=0)
        
        df_price["EBITDA / Market Capitalization"] = df_price["EBITDA TTM"] / df_price["Market Capitalization"] * 100
        df_price["EBITDA / Market Capitalization Lower Quintile"] = df_price["EBITDA / Market Capitalization"].rolling(1460).quantile(.15, interpolation = 'higher')
        df_price["EBITDA / Market Capitalization Upper Quintile"] = df_price["EBITDA / Market Capitalization"].rolling(1460).quantile(.85, interpolation = 'higher')
        
        # Free Cash Flow / MCap With Quantiles
        df_fcf = df_CashFlowStatement[["Date","Free Cash Flow TTM"]]
        df_fcf = df_fcf.astype({"Date": 'datetime64[ns]'})
        df_price = df_price.merge(df_fcf, how = "left", left_on = "Date", right_on = "Date")
        df_price = df_price.ffill(axis = 0)
        df_price["FCF / Market Capitalization"] = df_price["Free Cash Flow TTM"] / df_price["Market Capitalization"] * 100
        df_price["Limit"] = df_price["FCF / Market Capitalization"].rolling(1460).quantile(.1, interpolation = 'midpoint')
        # df_price["FCF / Market Capitalization Upper Quintile"] = df_price["FCF / Market Capitalization"].rolling(1460).quantile(.9, interpolation = 'midpoint')
    
    
        df_boundarytest = df_price
        df_boundarytest["Value"] = df_boundarytest["FCF / Market Capitalization"]
        df_boundarytest["Daily Change"] = df_boundarytest["Close"].pct_change(1)
        df_boundarytest["Daily Change Norm"] = df_boundarytest["Daily Change"] + 1
        df_boundarytest["Prev Limit"] = df_boundarytest["Limit"].shift(1)
        df_boundarytest["Prev Value"] = df_boundarytest["Value"].shift(1)
        #df_boundarytest["Signal"] = ("Green").where(df_boundarytest["Prev Value"] < df_boundarytest["Prev Limit"], "Red")
        
        df_fcf_green = df_boundarytest[
            (df_boundarytest["Prev Value"] > df_boundarytest["Prev Limit"])]
        df_fcf_red = df_boundarytest[
            (df_boundarytest["Prev Value"] < df_boundarytest["Prev Limit"])]
        
        prod_fcf_green = df_fcf_green["Daily Change Norm"].prod()
        prod_fcf_red = df_fcf_red["Daily Change Norm"].prod()
        totreturn = (df_boundarytest["Close"].iloc[-1] / df_boundarytest["Close"].iloc[0])-1
        time.sleep(2)
    
    except:
        prod_fcf_green, prod_fcf_red, totreturn = 0,0,0
    
    data = [[ticker, prod_fcf_green, prod_fcf_red, totreturn]]
    df = pd.DataFrame(data, columns =["Ticker","FCF/MCap Above Boundary", "FCF/MCap Below Boundary", "Total Return"] )
    dflist.append(df)
 
df = pd.concat(dflist, axis = 0)
#%%

output = df[
    (df["FCF/MCap Above Boundary"] != 1) & (df["FCF/MCap Below Boundary"] != 1) & (df["FCF/MCap Above Boundary"] != 0)]

boundaryres_fcf_above_mean = output["FCF/MCap Above Boundary"].mean()
boundaryres_fcf_above_std = output["FCF/MCap Above Boundary"].std()
boundaryres_fcf_below_mean = output["FCF/MCap Below Boundary"].mean()
boundaryres_fcf_below_mean_std = output["FCF/MCap Below Boundary"].std()

data = [[boundaryres_fcf_above_mean,boundaryres_fcf_above_std,boundaryres_fcf_below_mean,boundaryres_fcf_below_mean_std]]
df_output = pd.DataFrame(data, columns=["Above Limit (mean)", "Above Limit (StDev)", "Below Limit (mean)","Below Limit (StDev)"])
     