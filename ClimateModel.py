import requests
from bs4 import BeautifulSoup
import re
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import csv 
import os
import pickle
from IPython.display import display, HTML
import yfinance as yf
from sklearn.preprocessing import LabelEncoder
from dateutil.relativedelta import relativedelta
import matplotlib.dates as mdates

def load_corr_data():
    corr_data = pd.DataFrame()
    files = os.listdir("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country\\stock\\Corr") 
    for name in files:
        print(name)
        corr = pd.read_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country\\stock\\Corr\\" + name)
        country = name.split("_")[0]
        corr['Country'] = country
        corr = corr.query('Stock_Price != 1')
        corr.update(corr.fillna(0))
        corr_data = corr_data.append(corr)
    return(corr_data)


def load_climate_data():
    climate_data = pd.DataFrame()
    Fossil = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Fossil.csv')
    Fossil[3] = 'Fossil'
    climate_data = climate_data.append(Fossil)

    Deforestation = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Deforestation.csv')
    Deforestation[3] = 'Deforestation'
    climate_data = climate_data.append(Deforestation)

    GenderEquality = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Gender Equality.csv')
    GenderEquality[3] = 'GenderEquality'
    climate_data = climate_data.append(GenderEquality)

    Gun = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Gun.csv')
    Gun[3] = 'Gun'
    climate_data = climate_data.append(Gun)

    Political = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\political.csv')
    Political[3] = 'Political'
    climate_data = climate_data.append(Political)

    Prison = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Prison.csv')
    Prison[3] = 'Prison'
    climate_data = climate_data.append(Prison)

    Sealevel = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\sealevel.csv')
    Sealevel[3] = 'Sealevel'
    climate_data = climate_data.append(Sealevel)

    Tobacco = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Tobacco.csv')
    Tobacco[3] = 'Tobacco'
    climate_data = climate_data.append(Tobacco)

    War = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\war.csv')
    War[3] = 'War'
    climate_data = climate_data.append(War)

    Weapons = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\Weapons.csv')
    Weapons[3] = 'Weapons'
    climate_data = climate_data.append(Weapons)

    return(climate_data)

def load_portfolio(portfolio_name):
    portfolio = pd.DataFrame()
    portfolio = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\data\\{0}.csv'.format(portfolio_name))
    return (portfolio)

def project_empty_dataset(portfolio, year):  
    portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
    start_date_projection = portfolio['CreatedDate'].max()
    start_year = start_date_projection.year
    noOfYears = year - start_year
    noOfMonths = noOfYears * 12
    #print(noOfYears)
    projected_dates = []
    for month in range (noOfMonths):
        projected_dates.append(start_date_projection + relativedelta(months=+month))
    #print(projected_dates)
    precond_df = portfolio.query('CreatedDate ==\'' + str(start_date_projection)+ '\'')
    precond_df=precond_df.filter(items=['Company','Country','Ticker','Quantity','CreatedDate','Stock_Price','Invested_Value'])
    a_df=portfolio.filter(items=['Company','Country','Ticker','Quantity']).drop_duplicates()
    print(precond_df)
    a_df_temp = a_df.copy()
    a_df_temp['CreatedDate'] = datetime.now
    a_df_temp['Stock_Price'] = 0
    a_df_temp['Invested_Value'] = 0
    a_df_temp.drop(a_df_temp.index,inplace=True) 
    a_df_temp = a_df_temp.append(precond_df)
    #print(a_df_temp)
    for index,row in a_df.iterrows():
        print(row)
        for cd in projected_dates:
          a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':cd}, ignore_index=True)
    print(a_df_temp)


def increase_temp_model(portfolio, corr_data, climate_data, year):
    discount_rate = 0.05/12
    growth_rate = 0.09/12
    print(year)
    a_df=portfolio.filter(items=['Company','Country','Ticker','Quantity']).drop_duplicates()
    a_df_temp = a_df.copy()
    a_df_temp['CreatedDate'] = datetime.now
    a_df_temp['Stock_Price'] = 0
    a_df_temp['Invested_Value'] = 0
    a_df_temp.drop(a_df_temp.index,inplace=True) 
    start_date_projection = pd.to_datetime(portfolio['CreatedDate']).max()
    for index,row in a_df.iterrows():
        print(row)
        precond_df = portfolio.query('Country ==\''+ row['Country'] + '\' and Ticker==\'' + row['Ticker'] + '\'')
        precond_df['CreatedDate']= pd.to_datetime(precond_df['CreatedDate'])
        start_date_projection = precond_df['CreatedDate'].max()
        start_year = start_date_projection.year
        noOfYears = year - start_year
        noOfMonths = noOfYears * 12
        precond_df = precond_df.query('CreatedDate ==\'' + str(start_date_projection)+ '\'')
        precond_df=precond_df.filter(items=['Company','Country','Ticker','Quantity','CreatedDate','Stock_Price','Invested_Value'])
        a_df_temp = a_df_temp.append(precond_df)
        previousMonthDate = start_date_projection
        for month in range (noOfMonths):
            nextMonthDate = start_date_projection + relativedelta(months=+month)
            another_temp = a_df_temp.query('CreatedDate ==\'' + str(previousMonthDate)+ '\'')
            try:
                prevStockPrice = another_temp['Stock_Price'].iloc[0]
            except:
                #another_temp = a_df_temp.query('CreatedDate ==\'' + str(pd.to_datetime((a_df_temp['CreatedDate']).max()))+ '\'')
                #prevStockPrice = another_temp['Stock_Price'].iloc[0]
                continue
            query_fossil = climate_data.query('Ticker ==\'' + row['Ticker'] + '\'')
            print(query_fossil)
            if query_fossil.empty == False and query_fossil['Ticker'].iloc[0] == row['Ticker']:
                query_corr= corr_data.query('Country ==\'' + row['Country']+ '\'')
                query_corr = query_corr[query_corr['Measure'].str.contains("Fossil")]
                if query_corr.empty == True:
                    corr = 0
                else:
                    corr = query_corr['Stock_Price'].mean()
                    #if isinstance(corr, pd.Series):
                     #   corr = corr['Stock_Price'].mean()
                newStockPrice = prevStockPrice * (1 - corr - discount_rate + growth_rate)
            else:
                newStockPrice = prevStockPrice * (1 - discount_rate + growth_rate)
            a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':nextMonthDate,'Stock_Price':newStockPrice,'Invested_Value':row['Quantity'] * newStockPrice}, ignore_index=True)
            print(prevStockPrice)
            previousMonthDate = nextMonthDate
    print(a_df_temp)
    a_df_temp.to_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\projected_result_temp.csv")

def plot_projection( projection):
    print(projection)
    result_df = pd.DataFrame()
    projection_grouped = projection.groupby(['CreatedDate'])['Invested_Value'].sum()
    result_df = projection_grouped
      
    result_df.to_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\result_df_grouped.csv")
    result_df = pd.read_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\result_df_grouped.csv")
    #result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedMonth'] = result_df['CreatedDate'].dt.month
    result_df['CreatedYear'] = result_df['CreatedDate'].dt.year
    result_df['Created'] = result_df['CreatedYear'].astype(str) + ' : ' + result_df['CreatedMonth'].astype(str)
    result_df.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df_grouped = result_df.groupby(['Created'])['Invested_Value'].sum()
    
    result_df_grouped.to_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\result_df_grouped_1.csv")
    result_df_grouped = pd.read_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\result_df_grouped_1.csv")
    
    fig = plt.figure(figsize=(50, 20))
    ax = fig.add_subplot()
    #ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.plot(result_df_grouped.Created, result_df_grouped.Invested_Value)
    ax.set_ylabel("ROIC")
    ax.set_xlabel("Timeframe")
    ax.grid(True)
    fig.autofmt_xdate()
    plt.savefig('projection_plot.png',format='png')

corr_data = load_corr_data()
#print(corr_data)

climate_data = load_climate_data()
#print(climate_data)

portfolio = load_portfolio('portfolio')
#print(portfolio)



#project_empty_dataset(portfolio, 2026)
#increase_temp_model(portfolio,corr_data,climate_data,2024)

projection = pd.DataFrame()
projection = pd.read_csv('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\projected_result_temp.csv')

plot_projection(projection)

