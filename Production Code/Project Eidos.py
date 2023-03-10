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
import warnings

# Config
warnings.filterwarnings("ignore")
version_name = "Eidos"
version_number = "2.1 \n \n"
color_open = "\x1b["
color_close = "\x1b[0m"
color_green = "0;32;40m"
color_orange = "0;33;40m"
color_red = "0;31;40m"
color_blue = "0;34;40m"
color_white = "0;37;40m"
color_special_command = "3;37;40m"
    
# Set terminal view options
pd.set_option('display.max_rows', None) # set max number of rows to display to None (display all rows)
pd.set_option('display.max_columns', None) # set max number of columns to display to None (display all columns)
pd.set_option('display.width', 1000)

# Start of program
print("Booting "+version_name+" v "+version_number+"...")


print(
"""
========================================================================================================="""+color_open+color_orange+"""

8888888b.                   d8b                   888         8888888888 d8b      888     
888   Y88b                  Y8P                   888         888        Y8P      888    
888    888                                        888         888                 888                      
888   d88P 888d888 .d88b.  8888  .d88b.   .d8888b 888888      8888888    888  .d88888  .d88b.  .d8888b  
8888888P"  888P"  d88""88b "888 d8P  Y8b d88P"    888         888        888 d88" 888 d88""88b 88K  
888        888    888  888  888 88888888 888      888         888        888 888  888 888  888 "Y8888b.
888        888    Y88..88P  888 Y8b.     Y88b.    Y88b.       888        888 Y88b 888 Y88..88P      X88  
888        888     "Y88P"   888  "Y8888   "Y8888P  "Y888      8888888888 888  "Y88888  "Y88P"   88888P'
                            888  """   +color_close+"""                      
======================== """+color_open+color_orange+"  d88P  "+color_close+"""=======================================================================                             
                         """+color_open+color_orange+"888P"+color_close+"\n")

                            
#%% Preparing Datasets
df_tickers = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__tickers.csv")
    

#%% Calculations - Revenue

def eidos_revenue_old():
    # Get Data
    dataset_revenue = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__revenue.csv")
    # Calculate Pearson R for Revenue
    
    tickerlist = dataset_revenue["Ticker"].unique().tolist()
    pearson_list = []
    
    print("Retrieving Pearson Scores for Revenue...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_revenue = dataset_revenue[(dataset_revenue["Ticker"] == ticker)]
        df_pearson_revenue = df_pearson_revenue.reset_index(drop=True)
        try:
            df_pearson_revenue = [[ticker, stats.pearsonr(df_pearson_revenue.index,df_pearson_revenue["TTM Revenue"]).statistic, stats.pearsonr(df_pearson_revenue.index,df_pearson_revenue["TTM Revenue"]).pvalue, max(df_pearson_revenue.index)+1]]
        except:
            df_pearson_revenue = [[ticker,0,0,0]]
             
        df_pearson_revenue = pd.DataFrame(df_pearson_revenue, columns = ["Ticker", "Pearson R", "Pearson P-Value", "Pearson QNum"])
        pearson_list.append(df_pearson_revenue)
     
        
        # Calculating Spearman's Rho for EPS
        
    spearman_list = []
    
    print("\n Retrieving Spearman Scores for Revenue...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_revenue = dataset_revenue[(dataset_revenue["Ticker"] == ticker)]
        df_spearman_revenue = df_spearman_revenue.reset_index(drop=True)
        try:
            df_spearman_revenue = [[ticker, stats.spearmanr(df_spearman_revenue.index,df_spearman_revenue["TTM Revenue"]).statistic, stats.spearmanr(df_spearman_revenue.index,df_spearman_revenue["TTM Revenue"]).pvalue, max(df_spearman_revenue.index)+1]]
        except:
            df_spearman_revenue = [[ticker,0,0,0]]
        df_spearman_revenue = pd.DataFrame(df_spearman_revenue, columns = ["Ticker", "Spearman R", "Spearman P-Value", "Spearman QNum"])
    
        spearman_list.append(df_spearman_revenue)
     
        
    # Concatenate dataframes
    df_revenue_spearman = pd.concat(spearman_list, axis = 0)
    df_revenue_pearson = pd.concat(pearson_list, axis = 0)   
    
    
    # Create Scoresheet
    df_spearman = df_tickers.merge(df_revenue_spearman, how = "left", left_on = "ticker", right_on = "Ticker").dropna()
    df_spearman = df_spearman[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Spearman R","Spearman P-Value", "Spearman QNum"]]
    
    df_pearson = df_tickers.merge(df_revenue_pearson, how = "left", left_on = "ticker", right_on = "Ticker").dropna()
    df_pearson = df_pearson[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Pearson R","Pearson P-Value", "Pearson QNum"]]
    
    df_eidos = df_pearson.merge(df_spearman, how ="inner", left_on = "Ticker", right_on = "Ticker", copy = False, suffixes = ("","_copy"))
    df_eidos = df_eidos[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Pearson R","Pearson P-Value", "Pearson QNum","Spearman R","Spearman P-Value", "Spearman QNum"]]
    df_eidos = df_eidos[df_eidos["Pearson R"]>0]
    df_eidos = df_eidos[df_eidos["Spearman R"]>0]
    df_eidos = df_eidos[df_eidos["Spearman QNum"]>10]
    df_eidos = df_eidos[df_eidos["Pearson P-Value"]<0.1]
    df_eidos = df_eidos[df_eidos["Spearman P-Value"]<0.1]
    df_eidos["Score MULT"] = df_eidos["Pearson R"] * df_eidos["Spearman R"]
    df_eidos = df_eidos.sort_values(by=("Score MULT"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)
    
    # Create output
    
    sectorlist = df_eidos["Sector"].unique().tolist()
    
    for i in range(len(sectorlist)):
        sector = sectorlist[i]
        df = df_eidos[df_eidos.Sector == sector]
        df = df.sort_values(by=("Score MULT"), ascending = False).head(5)
        df = df.rename(columns = {"Score MULT":"Score"}).reset_index(drop=True)
        df["Score"] = round(df["Score"]*100,2)
        df = df[["Ticker","Company","Sector","Industry","Score"]]
        print(sector+":")
        print(df)
        print("\n")




def eidos_revenue():
    # Get Data
    dataset_revenue = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__revenue.csv")
    
    tickerlist = dataset_revenue["Ticker"].unique().tolist()
    pearson_list = []
    
    print("\n Retrieving Pearson Scores for Revenue...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_revenue = dataset_revenue[(dataset_revenue["Ticker"] == ticker)]
        df_pearson_revenue.reset_index(drop=True, inplace = True)
        try:
            df_pearson_revenue = [[ticker, stats.pearsonr(df_pearson_revenue.index,df_pearson_revenue["TTM Revenue"]).statistic, stats.pearsonr(df_pearson_revenue.index,df_pearson_revenue["TTM Revenue"]).pvalue, max(df_pearson_revenue.index)+1]]
        except:
            pass

             
        df_pearson_revenue = pd.DataFrame(df_pearson_revenue, columns = ["Ticker", "Pearson R", "Pearson P", "Pearson QNum"])
        pearson_list.append(df_pearson_revenue)
     
        
    spearman_list = []
    
    print("\n Retrieving Spearman Scores for Revenue...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_revenue = dataset_revenue[(dataset_revenue["Ticker"] == ticker)]
        df_spearman_revenue.reset_index(drop=True, inplace = True)
        try:
            df_spearman_revenue = [[ticker, stats.spearmanr(df_spearman_revenue.index,df_spearman_revenue["TTM Revenue"]).statistic, stats.spearmanr(df_spearman_revenue.index,df_spearman_revenue["TTM Revenue"]).pvalue, max(df_spearman_revenue.index)+1]]
        except:
            #df_spearman_revenue = [[ticker,0,0,0]]
            pass
        df_spearman_revenue = pd.DataFrame(df_spearman_revenue, columns = ["Ticker", "Spearman R", "Spearman P", "Spearman QNum"])
    
        spearman_list.append(df_spearman_revenue)
        
    # Concatenate dataframes
    df_spearman_revenue = pd.concat(spearman_list, axis = 0)
    df_pearson_revenue = pd.concat(pearson_list, axis = 0)   
    
    # Create Scoresheet
    df_eidos = df_tickers.merge(df_spearman_revenue, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Spearman", ""))
    df_eidos = df_eidos.merge(df_pearson_revenue, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Pearson", ""))
    df_eidos = df_eidos[["Ticker", "comp_name_2", "sector", "zacks_x_ind_desc", "Pearson R", "Pearson P", "Pearson QNum", "Spearman R", "Spearman P", "Spearman QNum"]]
    
    df_eidos = df_eidos.loc[(df_eidos["Pearson R"] > 0) & (df_eidos["Spearman R"] > 0) & (df_eidos["Spearman QNum"] > 20) & (df_eidos["Pearson P"] < 0.1) & (df_eidos["Spearman P"] < 0.1) ]
    df_eidos["Score"] = round(df_eidos["Pearson R"] * df_eidos["Spearman R"] * 100,2) 
    df_eidos = df_eidos.sort_values(by=("Score"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

    df_gold_revenue = df_eidos[df_eidos["Score"] > 90][["Ticker", "Company", "Sector", "Industry", "Score"]]
    print("\n \n We were able to locate " + str(len(df_gold_revenue)-1) + " Revenue Gold candidates:")
    print(df_gold_revenue)
        
#%% Calculations - Net Income

def eidos_netinc_old():
    # Get Data
    dataset_netinc = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__netinc.csv")
    # Calculate Pearson R for Revenue
    
    tickerlist = dataset_netinc["Ticker"].unique().tolist()
    pearson_list = []
    
    print("Retrieving Pearson Scores for Net Income...")
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
     
        
        # Calculating Spearman's Rho for EPS
        
    spearman_list = []
    
    print("\n Retrieving Spearman Scores for Net Income...") 
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
    df_ni_pearson = pd.concat(pearson_list, axis = 0)   
    
    
    # Create Scoresheet
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
    df_eidos = df_eidos.sort_values(by=("Score MULT"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)
    
    # Create output
    
    sectorlist = df_eidos["Sector"].unique().tolist()
    
    for i in range(len(sectorlist)):
        sector = sectorlist[i]
        df = df_eidos[df_eidos.Sector == sector]
        df = df.sort_values(by=("Score MULT"), ascending = False).head(5)
        df = df.rename(columns = {"Score MULT":"Score"}).reset_index(drop=True)
        df["Score"] = round(df["Score"]*100,2)
        df = df[["Ticker","Company","Sector","Industry","Score"]]
        print(sector+":")
        print(df)
        print("\n")
        
        
        
def eidos_netinc():
    # Get Data
    dataset_netinc = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__netinc.csv")
    # Calculate Pearson R for Revenue
    
    tickerlist = dataset_netinc["Ticker"].unique().tolist()
    
    pearson_list = []
    print("\n Retrieving Pearson Scores for Net Income...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_netinc = dataset_netinc[(dataset_netinc["Ticker"] == ticker)]
        df_pearson_netinc.reset_index(drop=True, inplace = True)
        try:
            df_pearson_netinc = [[ticker, stats.pearsonr(df_pearson_netinc.index,df_pearson_netinc["TTM Net Income"]).statistic, stats.pearsonr(df_pearson_netinc.index,df_pearson_netinc["TTM Net Income"]).pvalue, max(df_pearson_netinc.index)+1]]
        except:
            pass
             
        df_pearson_netinc = pd.DataFrame(df_pearson_netinc, columns = ["Ticker", "Pearson R", "Pearson P", "Pearson QNum"])
        pearson_list.append(df_pearson_netinc)
     
        
    spearman_list = []
    print("\n Retrieving Spearman Scores for Net Income...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_netinc = dataset_netinc[(dataset_netinc["Ticker"] == ticker)]
        df_spearman_netinc.reset_index(drop=True, inplace = True)
        try:
            df_spearman_netinc = [[ticker, stats.spearmanr(df_spearman_netinc.index,df_spearman_netinc["TTM Net Income"]).statistic, stats.spearmanr(df_spearman_netinc.index,df_spearman_netinc["TTM Net Income"]).pvalue, max(df_spearman_netinc.index)+1]]
        except:
            pass
        
        df_spearman_netinc = pd.DataFrame(df_spearman_netinc, columns = ["Ticker", "Spearman R", "Spearman P", "Spearman QNum"])
        spearman_list.append(df_spearman_netinc)
        
    # Concatenate dataframes
    df_spearman_netinc = pd.concat(spearman_list, axis = 0)
    df_pearson_netinc = pd.concat(pearson_list, axis = 0)   
    
    # Create Scoresheet
    df_eidos = df_tickers.merge(df_spearman_netinc, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Spearman", ""))
    df_eidos = df_eidos.merge(df_pearson_netinc, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Pearson", ""))
    df_eidos = df_eidos[["Ticker", "comp_name_2", "sector", "zacks_x_ind_desc", "Pearson R", "Pearson P", "Pearson QNum", "Spearman R", "Spearman P", "Spearman QNum"]]
    
    df_eidos = df_eidos.loc[(df_eidos["Pearson R"] > 0) & (df_eidos["Spearman R"] > 0) & (df_eidos["Spearman QNum"] > 20) & (df_eidos["Pearson P"] < 0.1) & (df_eidos["Spearman P"] < 0.1) ]
    df_eidos["Score"] = round(df_eidos["Pearson R"] * df_eidos["Spearman R"] * 100,2) 
    df_eidos = df_eidos.sort_values(by=("Score"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

    df_gold_netinc = df_eidos[df_eidos["Score"] > 90][["Ticker", "Company", "Sector", "Industry", "Score"]]
    print("\n \n We were able to locate " + str(len(df_gold_netinc)-1) + " Net Income Gold candidates:")
    print(df_gold_netinc)

#%% Calculations - EPS

def eidos_eps_old():
    # Get Data
    dataset_eps = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__eps.csv")
    # Calculate Pearson R for Revenue
    
    tickerlist = dataset_eps["Ticker"].unique().tolist()
    pearson_list = []
    
    print("Retrieving Pearson Scores for EPS...")
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
     
        
        # Calculating Spearman's Rho for EPS
        
    spearman_list = []
    
    print("\n Retrieving Spearman Scores for EPS...") 
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
    df_eps_pearson = pd.concat(pearson_list, axis = 0)   
    
    
    # Create Scoresheet
    df_spearman = df_tickers.merge(df_eps_spearman, how = "left", left_on = "ticker", right_on = "Ticker").dropna()
    df_spearman = df_spearman[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Spearman R","Spearman P-Value", "Spearman QNum"]]
    
    df_pearson = df_tickers.merge(df_eps_pearson, how = "left", left_on = "ticker", right_on = "Ticker").dropna()
    df_pearson = df_pearson[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Pearson R","Pearson P-Value", "Pearson QNum"]]
    
    df_eidos = df_pearson.merge(df_spearman, how ="inner", left_on = "Ticker", right_on = "Ticker", copy = False, suffixes = ("","_copy"))
    df_eidos = df_eidos[["Ticker","comp_name_2","sector","zacks_x_ind_desc","Pearson R","Pearson P-Value", "Pearson QNum","Spearman R","Spearman P-Value", "Spearman QNum"]]
    df_eidos = df_eidos[df_eidos["Pearson R"]>0]
    df_eidos = df_eidos[df_eidos["Spearman R"]>0]
    df_eidos = df_eidos[df_eidos["Spearman QNum"]>10]
    df_eidos = df_eidos[df_eidos["Pearson P-Value"]<0.1]
    df_eidos = df_eidos[df_eidos["Spearman P-Value"]<0.1]
    df_eidos["Score MULT"] = df_eidos["Pearson R"] * df_eidos["Spearman R"]
    df_eidos = df_eidos.sort_values(by=("Score MULT"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)
    
    # Create output
    
    sectorlist = df_eidos["Sector"].unique().tolist()
    
    for i in range(len(sectorlist)):
        sector = sectorlist[i]
        df = df_eidos[df_eidos.Sector == sector]
        df = df.sort_values(by=("Score MULT"), ascending = False).head(5)
        df = df.rename(columns = {"Score MULT":"Score"}).reset_index(drop=True)
        df["Score"] = round(df["Score"]*100,2)
        df = df[["Ticker","Company","Sector","Industry","Score"]]
        print(sector+":")
        print(df)
        print("\n")
        
        
def eidos_eps():
    # Get Data
    dataset_eps = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__eps.csv")
    # Calculate Pearson R for Revenue
   
    tickerlist = dataset_eps["Ticker"].unique().tolist()
    
    pearson_list = []
    print("\n Retrieving Pearson Scores for EPS...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_eps = dataset_eps[(dataset_eps["Ticker"] == ticker)]
        df_pearson_eps.reset_index(drop=True, inplace = True)
        try:
            df_pearson_eps = [[ticker, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).statistic, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).pvalue, max(df_pearson_eps.index)+1]]
        except:
            pass
             
        df_pearson_eps = pd.DataFrame(df_pearson_eps, columns = ["Ticker", "Pearson R", "Pearson P", "Pearson QNum"])
        pearson_list.append(df_pearson_eps)
     
        
    spearman_list = []
    print("\n Retrieving Spearman Scores for EPS...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_eps = dataset_eps[(dataset_eps["Ticker"] == ticker)]
        df_spearman_eps.reset_index(drop=True, inplace = True)
        try:
            df_spearman_eps = [[ticker, stats.spearmanr(df_spearman_eps.index,df_spearman_eps["TTM EPS"]).statistic, stats.spearmanr(df_spearman_eps.index,df_spearman_eps["TTM EPS"]).pvalue, max(df_spearman_eps.index)+1]]
        except:
            pass
        
        df_spearman_eps = pd.DataFrame(df_spearman_eps, columns = ["Ticker", "Spearman R", "Spearman P", "Spearman QNum"])
        spearman_list.append(df_spearman_eps)
        
    # Concatenate dataframes
    df_spearman_eps = pd.concat(spearman_list, axis = 0)
    df_pearson_eps = pd.concat(pearson_list, axis = 0)   
    
    # Create Scoresheet
    df_eidos = df_tickers.merge(df_spearman_eps, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Spearman", ""))
    df_eidos = df_eidos.merge(df_pearson_eps, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Pearson", ""))
    df_eidos = df_eidos[["Ticker", "comp_name_2", "sector", "zacks_x_ind_desc", "Pearson R", "Pearson P", "Pearson QNum", "Spearman R", "Spearman P", "Spearman QNum"]]
    
    df_eidos = df_eidos.loc[(df_eidos["Pearson R"] > 0) & (df_eidos["Spearman R"] > 0) & (df_eidos["Spearman QNum"] > 20) & (df_eidos["Pearson P"] < 0.1) & (df_eidos["Spearman P"] < 0.1) ]
    df_eidos["Score"] = round(df_eidos["Pearson R"] * df_eidos["Spearman R"] * 100,2) 
    df_eidos = df_eidos.sort_values(by=("Score"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

    df_gold_eps = df_eidos[df_eidos["Score"] > 90][["Ticker", "Company", "Sector", "Industry", "Score"]]
    print("\n \n We were able to locate " + str(len(df_gold_eps)-1) + " EPS Gold candidates:")
    print(df_gold_eps)
    
#%% Calculations - Triple Triad

def eidos_triple():
# Fetch Revenue Table
    # Get Data
    dataset_revenue = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__revenue.csv")
    
    tickerlist = dataset_revenue["Ticker"].unique().tolist()
    pearson_list = []
    
    print("\n Retrieving Pearson Scores for Revenue...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_revenue = dataset_revenue[(dataset_revenue["Ticker"] == ticker)]
        df_pearson_revenue.reset_index(drop=True, inplace = True)
        try:
            df_pearson_revenue = [[ticker, stats.pearsonr(df_pearson_revenue.index,df_pearson_revenue["TTM Revenue"]).statistic, stats.pearsonr(df_pearson_revenue.index,df_pearson_revenue["TTM Revenue"]).pvalue, max(df_pearson_revenue.index)+1]]
        except:
            pass

             
        df_pearson_revenue = pd.DataFrame(df_pearson_revenue, columns = ["Ticker", "Pearson R", "Pearson P", "Pearson QNum"])
        pearson_list.append(df_pearson_revenue)
     
        
    spearman_list = []
    
    print("\n Retrieving Spearman Scores for Revenue...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_revenue = dataset_revenue[(dataset_revenue["Ticker"] == ticker)]
        df_spearman_revenue.reset_index(drop=True, inplace = True)
        try:
            df_spearman_revenue = [[ticker, stats.spearmanr(df_spearman_revenue.index,df_spearman_revenue["TTM Revenue"]).statistic, stats.spearmanr(df_spearman_revenue.index,df_spearman_revenue["TTM Revenue"]).pvalue, max(df_spearman_revenue.index)+1]]
        except:
            #df_spearman_revenue = [[ticker,0,0,0]]
            pass
        df_spearman_revenue = pd.DataFrame(df_spearman_revenue, columns = ["Ticker", "Spearman R", "Spearman P", "Spearman QNum"])
    
        spearman_list.append(df_spearman_revenue)
        
    # Concatenate dataframes
    df_spearman_revenue = pd.concat(spearman_list, axis = 0)
    df_pearson_revenue = pd.concat(pearson_list, axis = 0)   
    
    # Create Scoresheet
    df_eidos = df_tickers.merge(df_spearman_revenue, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Spearman", ""))
    df_eidos = df_eidos.merge(df_pearson_revenue, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Pearson", ""))
    df_eidos = df_eidos[["Ticker", "comp_name_2", "sector", "zacks_x_ind_desc", "Pearson R", "Pearson P", "Pearson QNum", "Spearman R", "Spearman P", "Spearman QNum"]]
    
    df_eidos = df_eidos.loc[(df_eidos["Pearson R"] > 0) & (df_eidos["Spearman R"] > 0) & (df_eidos["Spearman QNum"] > 20) & (df_eidos["Pearson P"] < 0.1) & (df_eidos["Spearman P"] < 0.1) ]
    df_eidos["Score"] = round(df_eidos["Pearson R"] * df_eidos["Spearman R"] * 100,2) 
    df_eidos = df_eidos.sort_values(by=("Score"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

    df_gold_revenue = df_eidos[df_eidos["Score"] > 90][["Ticker", "Company", "Sector", "Industry", "Score"]]

# Fetch Net Income Table
    # Get Data
    dataset_netinc = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__netinc.csv")
    # Calculate Pearson R for Revenue
    
    tickerlist = dataset_netinc["Ticker"].unique().tolist()
    
    pearson_list = []
    print("\n Retrieving Pearson Scores for Net Income...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_netinc = dataset_netinc[(dataset_netinc["Ticker"] == ticker)]
        df_pearson_netinc.reset_index(drop=True, inplace = True)
        try:
            df_pearson_netinc = [[ticker, stats.pearsonr(df_pearson_netinc.index,df_pearson_netinc["TTM Net Income"]).statistic, stats.pearsonr(df_pearson_netinc.index,df_pearson_netinc["TTM Net Income"]).pvalue, max(df_pearson_netinc.index)+1]]
        except:
            pass
             
        df_pearson_netinc = pd.DataFrame(df_pearson_netinc, columns = ["Ticker", "Pearson R", "Pearson P", "Pearson QNum"])
        pearson_list.append(df_pearson_netinc)
     
        
    spearman_list = []
    print("\n Retrieving Spearman Scores for Net Income...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_netinc = dataset_netinc[(dataset_netinc["Ticker"] == ticker)]
        df_spearman_netinc.reset_index(drop=True, inplace = True)
        try:
            df_spearman_netinc = [[ticker, stats.spearmanr(df_spearman_netinc.index,df_spearman_netinc["TTM Net Income"]).statistic, stats.spearmanr(df_spearman_netinc.index,df_spearman_netinc["TTM Net Income"]).pvalue, max(df_spearman_netinc.index)+1]]
        except:
            pass
        
        df_spearman_netinc = pd.DataFrame(df_spearman_netinc, columns = ["Ticker", "Spearman R", "Spearman P", "Spearman QNum"])
        spearman_list.append(df_spearman_netinc)
        
    # Concatenate dataframes
    df_spearman_netinc = pd.concat(spearman_list, axis = 0)
    df_pearson_netinc = pd.concat(pearson_list, axis = 0)   
    
    # Create Scoresheet
    df_eidos = df_tickers.merge(df_spearman_netinc, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Spearman", ""))
    df_eidos = df_eidos.merge(df_pearson_netinc, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Pearson", ""))
    df_eidos = df_eidos[["Ticker", "comp_name_2", "sector", "zacks_x_ind_desc", "Pearson R", "Pearson P", "Pearson QNum", "Spearman R", "Spearman P", "Spearman QNum"]]
    
    df_eidos = df_eidos.loc[(df_eidos["Pearson R"] > 0) & (df_eidos["Spearman R"] > 0) & (df_eidos["Spearman QNum"] > 20) & (df_eidos["Pearson P"] < 0.1) & (df_eidos["Spearman P"] < 0.1) ]
    df_eidos["Score"] = round(df_eidos["Pearson R"] * df_eidos["Spearman R"] * 100,2) 
    df_eidos = df_eidos.sort_values(by=("Score"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

    df_gold_netinc = df_eidos[df_eidos["Score"] > 90][["Ticker", "Company", "Sector", "Industry", "Score"]]
    
# Fetch EPS Table
    # Get Data
    dataset_eps = pd.read_csv("C:/Users/eirik/OneDrive/Documents/Cloudkit/Database/master__eps.csv")
    # Calculate Pearson R for Revenue
   
    tickerlist = dataset_eps["Ticker"].unique().tolist()
    
    pearson_list = []
    print("\n Retrieving Pearson Scores for EPS...")
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_pearson_eps = dataset_eps[(dataset_eps["Ticker"] == ticker)]
        df_pearson_eps.reset_index(drop=True, inplace = True)
        try:
            df_pearson_eps = [[ticker, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).statistic, stats.pearsonr(df_pearson_eps.index,df_pearson_eps["TTM EPS"]).pvalue, max(df_pearson_eps.index)+1]]
        except:
            pass
             
        df_pearson_eps = pd.DataFrame(df_pearson_eps, columns = ["Ticker", "Pearson R", "Pearson P", "Pearson QNum"])
        pearson_list.append(df_pearson_eps)
     
        
    spearman_list = []
    print("\n Retrieving Spearman Scores for EPS...") 
    for i in tqdm(range(len(tickerlist))):
        ticker = tickerlist[i]
        df_spearman_eps = dataset_eps[(dataset_eps["Ticker"] == ticker)]
        df_spearman_eps.reset_index(drop=True, inplace = True)
        try:
            df_spearman_eps = [[ticker, stats.spearmanr(df_spearman_eps.index,df_spearman_eps["TTM EPS"]).statistic, stats.spearmanr(df_spearman_eps.index,df_spearman_eps["TTM EPS"]).pvalue, max(df_spearman_eps.index)+1]]
        except:
            pass
        
        df_spearman_eps = pd.DataFrame(df_spearman_eps, columns = ["Ticker", "Spearman R", "Spearman P", "Spearman QNum"])
        spearman_list.append(df_spearman_eps)
        
    # Concatenate dataframes
    df_spearman_eps = pd.concat(spearman_list, axis = 0)
    df_pearson_eps = pd.concat(pearson_list, axis = 0)   
    
    # Create Scoresheet
    df_eidos = df_tickers.merge(df_spearman_eps, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Spearman", ""))
    df_eidos = df_eidos.merge(df_pearson_eps, how="left", left_on="ticker", right_on="Ticker", suffixes=("_Pearson", ""))
    df_eidos = df_eidos[["Ticker", "comp_name_2", "sector", "zacks_x_ind_desc", "Pearson R", "Pearson P", "Pearson QNum", "Spearman R", "Spearman P", "Spearman QNum"]]
    
    df_eidos = df_eidos.loc[(df_eidos["Pearson R"] > 0) & (df_eidos["Spearman R"] > 0) & (df_eidos["Spearman QNum"] > 20) & (df_eidos["Pearson P"] < 0.1) & (df_eidos["Spearman P"] < 0.1) ]
    df_eidos["Score"] = round(df_eidos["Pearson R"] * df_eidos["Spearman R"] * 100,2) 
    df_eidos = df_eidos.sort_values(by=("Score"), ascending = False)
    df_eidos = df_eidos.rename(columns = {"comp_name_2":"Company","sector":"Sector","zacks_x_ind_desc":"Industry"}).reset_index(drop=True)

    df_gold_eps = df_eidos[df_eidos["Score"] > 90][["Ticker", "Company", "Sector", "Industry", "Score"]]
    
    
    # Merge dataframes
    df_triple = pd.merge(df_gold_revenue, df_gold_netinc, on = 'Ticker', how = 'inner')
    df_triple = pd.merge(df_triple, df_gold_eps, on = 'Ticker', how = 'inner')
    df_triple = df_triple[["Ticker","Company","Industry","Score_x","Score_y","Score"]]
    df_triple = df_triple.rename(columns = {"Score_x":"Revenue Score","Score_y":"Net Income Score","Score":"EPS Score"})

    print("\n \n We were able to locate " + str(len(df_triple)-1) + " Triple Triad Gold candidates:")
    print(df_triple)
    
    
#%% Run Software

menu_item_1 = int(input("What metric would you like to sort by?\n\n"
                            "1. Revenue\n"
                            "2. Net Income \n"
                            "3. EPS \n"
                            "4. Triple Triad \n"
                            "------------------ \n"
                            +color_open+color_special_command+"0. Exit Program"+color_close+"\n\n"))


if menu_item_1 == 0:
    print("Exiting...")

elif menu_item_1 == 1:
    eidos_revenue()
    
elif menu_item_1 == 2:
    eidos_netinc()
    
elif menu_item_1 == 3:
    eidos_eps()
    
elif menu_item_1 == 4:
    eidos_triple()
    
else:
    print("Number not in range..... Exiting with failure")
    
    
#%% Model Validation
