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

warnings.filterwarnings("ignore")


#%% Inputs

ticker = "MSFT"


#%% Preparations
yf_ticker = yf.Ticker(ticker)
start_date = "2017-01-01"
master_tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Research Code/Research Resources/Tickers.csv") 
meta_stock = master_tickers.loc[master_tickers['ticker'] == ticker]
company = meta_stock["comp_name"].values
company = np.array2string(company).replace("[","").replace("]","").replace("'","")


# Resources
mt =          "https://www.macrotrends.net/stocks/charts/"
revenue =     "{base}{ticker}/{company}/revenue".format(ticker=ticker,company=company,base=mt)
netinc =      "{base}{ticker}/{company}/net-income".format(ticker=ticker,company=company,base=mt)
eps =         "{base}{ticker}/{company}/eps-earnings-per-share-diluted".format(ticker=ticker,company=company,base=mt) 
fcf =         "{base}{ticker}/{company}/free-cash-flow".format(ticker=ticker,company=company,base=mt)
shares =      "{base}{ticker}/{company}/shares-outstanding".format(ticker=ticker,company=company,base=mt)
roe =         "{base}{ticker}/{company}/roe".format(ticker=ticker,company=company,base=mt)
roi =         "{base}{ticker}/{company}/roi".format(ticker=ticker,company=company,base=mt)
roa =         "{base}{ticker}/{company}/roa".format(ticker=ticker,company=company,base=mt)
shequity =    "{base}{ticker}/{company}/total-share-holder-equity".format(ticker=ticker,company=company,base=mt)
grossmarg =   "{base}{ticker}/{company}/gross-margin".format(ticker=ticker,company=company,base=mt)
opermarg =    "{base}{ticker}/{company}/operating-margin".format(ticker=ticker,company=company,base=mt)
netmarg =     "{base}{ticker}/{company}/net-profit-margin".format(ticker=ticker,company=company,base=mt)
opex =        "{base}{ticker}/{company}/operating-expenses".format(ticker=ticker,company=company,base=mt)
rnd =         "{base}{ticker}/{company}/research-development-expenses".format(ticker=ticker,company=company,base=mt)

# ADDED v1.0
cash =        "{base}{ticker}/{company}/cash-on-hand".format(ticker=ticker,company=company,base=mt)
debt =        "{base}{ticker}/{company}/long-term-debt".format(ticker=ticker,company=company,base=mt)


#%% Data Ingestions

# Quarterly Data (where Q and A are available)
  # 0 for Annual, 1 for Quarterly
Q_Revenue   = pd.read_html(revenue)[1] 
Q_NetInc    = pd.read_html(netinc)[1] 
Q_Eps       = pd.read_html(eps)[1] 
Q_Fcf       = pd.read_html(fcf)[1] 
Q_Shares    = pd.read_html(shares)[1]
Q_ShEquity  = pd.read_html(shequity)[1] 
Q_OpEx      = pd.read_html(opex)[1]
Q_RnD       = pd.read_html(rnd)[1]

# ADDED v1.0
Q_Cash      = pd.read_html(cash)[1]
Q_Debt      = pd.read_html(debt)[1]

# Quarterly Data (Rates where only Q are available)
  # 0 for Quarterly Data, 1 for Company Metadata
Q_Roe       = pd.read_html(roe)[0]
Q_Roi       = pd.read_html(roi)[0] 
Q_Roa       = pd.read_html(roa)[0] 
Q_GrossM    = pd.read_html(grossmarg)[0] 
Q_OperatingM = pd.read_html(opermarg)[0] 


# Revenue & TTM Revenue
Q_Revenue.columns = ['Date','Revenue'] # Rename cols
Q_Revenue["Revenue"] = Q_Revenue["Revenue"].str.replace("[$,]","",regex=True) # Removes commas and $ from revenues
Q_Revenue["Date"] = pd.to_datetime(Q_Revenue["Date"]) # converts date to datetime from object
Q_Revenue["Revenue"] = pd.to_numeric(Q_Revenue["Revenue"]) # converts revenue to float from object
Q_Revenue.sort_values("Date", inplace=True) # Sort dates by ascending
Q_Revenue["TTM Revenue"] = Q_Revenue["Revenue"].rolling(4).sum() # Creates trailing 12 month sum

# Revenue Pct Changes
Q_Revenue["Revenue QoQ"] = Q_Revenue['Revenue'].pct_change(1)
Q_Revenue["Revenue YoY"] = Q_Revenue['Revenue'].pct_change(4)

# TTM Revenue Pct Changes
Q_Revenue["TTM Revenue QoQ"] = Q_Revenue['TTM Revenue'].pct_change(1)
Q_Revenue["TTM Revenue YoY"] = Q_Revenue['TTM Revenue'].pct_change(4)
Q_Revenue["TTM Revenue 5Y CAGR"]  = ((Q_Revenue['TTM Revenue'].pct_change(20)+1)**0.2)-1
Q_Revenue = Q_Revenue[Q_Revenue["Date"]>start_date] # Snips data to target time frame


# EBITDA & TTM EBITDA
Q_NetInc.columns = ['Date','Net Income'] # Rename cols
Q_NetInc["Net Income"] = Q_NetInc["Net Income"].str.replace("[$,]","",regex=True) # Removes commas and $ from EBITDA
Q_NetInc["Date"] = pd.to_datetime(Q_NetInc["Date"]) # converts date to datetime from object
Q_NetInc["Net Income"] = pd.to_numeric(Q_NetInc["Net Income"]) # converts EBITDA to float from object
Q_NetInc.sort_values("Date", inplace=True) # Sort dates by ascending
Q_NetInc["TTM Net Income"] = Q_NetInc["Net Income"].rolling(4).sum() # Creates trailing 12 month sum

# EBITDA Pct Changes 
Q_NetInc["Net Income QoQ"] = Q_NetInc['Net Income'].pct_change(1)
Q_NetInc["Net Income YoY"] = Q_NetInc['Net Income'].pct_change(4)

# TTM EBITDA Pct Changes
Q_NetInc["TTM Net Income QoQ"] = Q_NetInc['TTM Net Income'].pct_change(1)
Q_NetInc["TTM Net Income YoY"] = Q_NetInc['TTM Net Income'].pct_change(4)
Q_NetInc["TTM Net Income 5Y CAGR"]  = ((Q_NetInc['TTM Net Income'].pct_change(20)+1)**0.2)-1
Q_NetInc = Q_NetInc[Q_NetInc["Date"]>start_date] # Snips data to target time frame


# EPS & TTM EPS
Q_Eps.columns = ['Date','EPS'] # Rename cols
Q_Eps["EPS"] = Q_Eps["EPS"].str.replace("[$,]","",regex=True) # Removes commas and $ from EPS
Q_Eps["Date"] = pd.to_datetime(Q_Eps["Date"]) # converts date to datetime from object
Q_Eps["EPS"] = pd.to_numeric(Q_Eps["EPS"]) # converts EPS to float from object
Q_Eps.sort_values("Date", inplace=True) # Sort dates by ascending
Q_Eps["TTM EPS"] = Q_Eps["EPS"].rolling(4).sum() # Creates trailing 12 month sum

# EPS Pct Changes
Q_Eps["EPS QoQ"] = Q_Eps['EPS'].pct_change(1)
Q_Eps["EPS YoY"] = Q_Eps['EPS'].pct_change(4)

# TTM EPS Pct Changes
Q_Eps["TTM EPS QoQ"] = Q_Eps['TTM EPS'].pct_change(1)
Q_Eps["TTM EPS YoY"] = Q_Eps['TTM EPS'].pct_change(4)
Q_Eps["TTM EPS 5Y CAGR"]  = ((Q_Eps['TTM EPS'].pct_change(20)+1)**0.2)-1
Q_Eps = Q_Eps[Q_Eps["Date"]>start_date] # Snips data to target time frame


# FCF & TTM FCF
Q_Fcf.columns = ['Date','FCF'] # Rename cols
#Q_Fcf["FCF"] = Q_Fcf["FCF"].str.replace("[$,]","",regex=True) # Removes commas and $ from FCF
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


# Shares Outstanding
Q_Shares.columns = ['Date','Shares Outstanding'] # Rename cols
#Q_Shares["Shares Outstanding"] = Q_Shares["Shares Outstanding"].str.replace("[$,]","",regex=True) # Removes commas and $ from FCF
Q_Shares["Date"] = pd.to_datetime(Q_Shares["Date"]) # converts date to datetime from object
Q_Shares["Shares Outstanding"] = pd.to_numeric(Q_Shares["Shares Outstanding"]) # converts FCF to float from object
Q_Shares.sort_values("Date", inplace=True) # Sort dates by ascending

# FCF Pct Changes
Q_Shares["Shares Outstanding QoQ"] = Q_Shares['Shares Outstanding'].pct_change(1)
Q_Shares["Shares Outstanding YoY"] = Q_Shares['Shares Outstanding'].pct_change(4)
Q_Shares["Shares Outstanding 5Y CAGR"]  = ((Q_Shares['Shares Outstanding'].pct_change(20)+1)**0.2)-1
Q_Shares = Q_Shares[Q_Shares["Date"]>start_date] # Snips data to target time frame


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


# Net Shareholder Margin
Q_ShEquity.columns = ['Date','Net Shareholder Equity'] # Rename cols
Q_ShEquity["Net Shareholder Equity"] = Q_ShEquity["Net Shareholder Equity"].str.replace("[$,]","",regex=True) # Removes commas and $ from EPS
Q_ShEquity["Date"] = pd.to_datetime(Q_ShEquity["Date"]) # converts date to datetime from object
Q_ShEquity["Net Shareholder Equity"] = pd.to_numeric(Q_ShEquity["Net Shareholder Equity"]) # converts EPS to float from object
Q_ShEquity.sort_values("Date", inplace=True) # Sort dates by ascending

# EPS Pct Changes
Q_ShEquity["Net Shareholder Equity QoQ"] = Q_ShEquity['Net Shareholder Equity'].pct_change(1)
Q_ShEquity["Net Shareholder Equity YoY"] = Q_ShEquity['Net Shareholder Equity'].pct_change(4)
Q_ShEquity["Net Shareholder Equity 5Y CAGR"]  = ((Q_ShEquity['Net Shareholder Equity'].pct_change(20)+1)**0.2)-1
Q_ShEquity = Q_ShEquity[Q_ShEquity["Date"]>start_date] # Snips data to target time frame


# OpEx & TTM OpEx
Q_OpEx.columns = ['Date','OpEx'] # Rename cols
Q_OpEx["OpEx"] = Q_OpEx["OpEx"].str.replace("[$,]","",regex=True) # Removes commas and $ from EPS
Q_OpEx["Date"] = pd.to_datetime(Q_OpEx["Date"]) # converts date to datetime from object
Q_OpEx["OpEx"] = pd.to_numeric(Q_OpEx["OpEx"]) # converts EPS to float from object

Q_OpEx.sort_values("Date", inplace=True) # Sort dates by ascending
Q_OpEx["TTM OpEx"] = Q_OpEx["OpEx"].rolling(4).sum() # Creates trailing 12 month sum

# OpEx Pct Changes
Q_OpEx["OpEx QoQ"] = Q_OpEx['OpEx'].pct_change(1)
Q_OpEx["OpEx YoY"] = Q_OpEx['OpEx'].pct_change(4)

# TTM OpEx Pct Changes
Q_OpEx["TTM OpEx QoQ"] = Q_OpEx['TTM OpEx'].pct_change(1)
Q_OpEx["TTM OpEx YoY"] = Q_OpEx['TTM OpEx'].pct_change(4)
Q_OpEx["TTM OpEx 5Y CAGR"]  = ((Q_OpEx['TTM OpEx'].pct_change(20)+1)**0.2)-1

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

Q_OpEx = Q_OpEx[Q_OpEx["Date"]>start_date] # Snips data to target time frame
Q_RnD = Q_RnD[Q_RnD["Date"]>start_date] # Snips data to target time frame


# Cash on Hand
Q_Cash.columns = ['Date','Cash on Hand'] # Rename cols
Q_Cash["Cash on Hand"] = Q_Cash["Cash on Hand"].str.replace("[$,]","",regex=True) # Removes commas and $ from Cash on Hand
Q_Cash["Date"] = pd.to_datetime(Q_Cash["Date"]) # converts date to datetime from object
Q_Cash["Cash on Hand"] = pd.to_numeric(Q_Cash["Cash on Hand"]) # converts Cash on Hand to float from object
Q_Cash.sort_values("Date", inplace=True) # Sort dates by ascending

# Cash on Hand Pct Changes
Q_Cash["Cash on Hand QoQ"] = Q_Cash['Cash on Hand'].pct_change(1)
Q_Cash["Cash on Hand YoY"] = Q_Cash['Cash on Hand'].pct_change(4)
Q_Cash["Cash on Hand 5Y CAGR"]  = ((Q_Cash['Cash on Hand'].pct_change(20)+1)**0.2)-1
Q_Cash = Q_Cash[Q_Cash["Date"]>start_date] # Snips data to target time frame


# Long Term Debt
Q_Debt.columns = ['Date','Long Term Debt'] # Rename cols
if 1==1:
  try:
    Q_Debt["Long Term Debt"] = Q_Debt["Long Term Debt"].str.replace("[$,]","",regex=True) # Removes commas and $ from EPS
  except:
    pass
Q_Debt["Date"] = pd.to_datetime(Q_Debt["Date"]) # converts date to datetime from object
Q_Debt["Long Term Debt"] = pd.to_numeric(Q_Debt["Long Term Debt"]) # converts EPS to float from object
Q_Debt.sort_values("Date", inplace=True) # Sort dates by ascending

# EPS Pct Changes
Q_Debt["Long Term Debt QoQ"] = Q_Debt['Long Term Debt'].pct_change(1)
Q_Debt["Long Term Debt YoY"] = Q_Debt['Long Term Debt'].pct_change(4)
Q_Debt["Long Term Debt 5Y CAGR"]  = ((Q_Debt['Long Term Debt'].pct_change(20)+1)**0.2)-1
Q_Debt["Long Term Debt"] = -1*Q_Debt["Long Term Debt"]
Q_Debt = Q_Debt[Q_Debt["Date"]>start_date] # Snips data to target time frame


# Price Data
stock = yf.Ticker(ticker)
stock_all = stock.history(period="max")
D_HistoricalPrice = stock_all[["Close"]]

# SMA
D_HistoricalPrice["50d SMA"] = D_HistoricalPrice["Close"].rolling(window = 50).mean()
D_HistoricalPrice["250d SMA"] = D_HistoricalPrice["Close"].rolling(window = 250).mean()
D_HistoricalPrice = D_HistoricalPrice[D_HistoricalPrice.index>=start_date]


D_StockInfo = yf_ticker.info
D_StockInfo.items()

Info = []
Failed = []
Keys = ['sector', 'industry', 'country', 'longBusinessSummary','currentPrice','targetMeanPrice',
        'heldPercentInsiders','forwardPE','payoutRatio','trailingPE','dividendYield','numberOfAnalystOpinions',
        'totalCash','totalDebt','debtToEquity','enterpriseToRevenue','enterpriseToEbitda','52WeekChange',
        'heldPercentInstitutions','marketCap','averageVolume10days','longName']
for Key in Keys:
    try:
      Info.append(D_StockInfo[Key])
    except:
      Info.append(0)
      pass
    



D_Info = pd.DataFrame({'Category': Keys, 'Value': Info})

D_Info = D_Info.set_index('Category')
D_Info = D_Info.T


#%% Merge & Export

# Merge Quarterly Data
Quarterly_Data = Q_Revenue.merge(Q_NetInc, left_on='Date', right_on='Date')
Quarterly_Data = Quarterly_Data.merge(Q_Eps, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_Fcf, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_Shares, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_Roa, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_Roe, left_on = 'Date', right_on = 'Date')

if len(Q_Roi) > 0:
  Quarterly_Data = Quarterly_Data.merge(Q_Roi, left_on = 'Date', right_on = 'Date')
else:
  Quarterly_Data["ROI"] = ""
  Quarterly_Data["ROI QoQ"] = ""
  Quarterly_Data["ROI YoY"]  = ""
  Quarterly_Data["ROI 5Y CAGR"] = ""
  
Quarterly_Data = Quarterly_Data.merge(Q_GrossM, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_OperatingM, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_NetM, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_ShEquity, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_OpEx, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_RnD, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_Cash, left_on = 'Date', right_on = 'Date')
Quarterly_Data = Quarterly_Data.merge(Q_Debt, left_on = 'Date', right_on = 'Date')

# To Excel
with pd.ExcelWriter('Research Resources/BDR.xlsx') as writer:  
    Quarterly_Data.to_excel(writer, sheet_name='Quarterly Data')
    D_HistoricalPrice.to_excel(writer, sheet_name='Price Data')
    D_Info.to_excel(writer, sheet_name='Info') 