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
from datetime import date
import math

def load_corr_data():
    corr_data = pd.DataFrame()

    corr = pd.read_csv("data\\corr_master.csv")

    corr = corr.query('Stock_Price != 1')
    corr.update(corr.fillna(0))
    corr_data = corr
    return(corr_data)


def load_climate_data():
    climate_data = pd.DataFrame()
    climate_data = pd.read_csv('data\\climate_master.csv')
    return(climate_data)

def load_portfolio(portfolio_name):
    portfolio = pd.DataFrame()
    portfolio = pd.read_csv('data\\{0}.csv'.format(portfolio_name))
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
    last_date = date(year, 12, 31)
    
    for index,row in a_df.iterrows():
        print(row)
        precond_df = portfolio.query('Country ==\''+ row['Country'] + '\' and Ticker==\'' + row['Ticker'] + '\'')
        precond_df['CreatedDate']= pd.to_datetime(precond_df['CreatedDate'])
        start_date_projection = precond_df['CreatedDate'].max()
        start_year = start_date_projection.year
        noOfYears = year - start_year
        noOfMonths = noOfYears * 12
        r = relativedelta(start_date_projection, last_date)
        #noOfMonths = r.months
        precond_df = precond_df.query('CreatedDate ==\'' + str(start_date_projection)+ '\'')
        precond_df=precond_df.filter(items=['Company','Country','Ticker','Quantity','CreatedDate','Stock_Price','Invested_Value'])
        
        #a_df_temp = a_df_temp.append(precond_df)
        previousMonthDate = start_date_projection
        another_temp = precond_df.query('CreatedDate ==\'' + str(previousMonthDate)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')
        prevStockPrice = another_temp['Stock_Price'].iloc[0]
        for month in range (1, noOfMonths):
            nextMonthDate = start_date_projection + relativedelta(months=+month)
            another_temp = a_df_temp.query('CreatedDate ==\'' + str(previousMonthDate)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')
            try:
                if month != 1:
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
                newStockPrice = prevStockPrice * (1 - (corr/12) - discount_rate + growth_rate)
            else:
                newStockPrice = prevStockPrice * (1 - discount_rate + growth_rate)
            a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':nextMonthDate,'Stock_Price':newStockPrice,'Invested_Value':row['Quantity'] * newStockPrice}, ignore_index=True)
            print(prevStockPrice)
            previousMonthDate = nextMonthDate
    print(a_df_temp)
    a_df_temp = a_df_temp.append(portfolio)
    a_df_temp.to_csv("projected_result_temp.csv")

def calculate_SAD(latitude, CreatedDate):
    latitude = float(latitude)
    year, month, day = CreatedDate.split('-')
    day=day[:2]
    inside = 2 * 3.14 / 365 * (float(day) - 80.25)
    sun_inclination_angle = 0.4102 * math.sin(inside)
    Ht = 24 - (7.72 * (- math.tan(2 * 3.14 * latitude / 360) * math.tan(sun_inclination_angle)))
    SAD = Ht - 12
    #print(SAD/1000)
    return(SAD/(24*100))
    #return 0

def increase_temp_model_SAD(portfolio, corr_data, climate_data,discount_rate,growth_rate, year):
    discount_rate = discount_rate/12
    growth_rate = growth_rate/12
    print(year)
    a_df=portfolio.filter(items=['Company','Country','Ticker','Quantity','Latitude']).drop_duplicates()
    a_df_temp = a_df.copy()
    a_df_temp['CreatedDate'] = datetime.now
    a_df_temp['Stock_Price'] = 0
    a_df_temp['Invested_Value'] = 0
    a_df_temp.drop(a_df_temp.index,inplace=True) 
    start_date_projection = pd.to_datetime(portfolio['CreatedDate']).max()
    last_date = date(year, 12, 31)
    
    for index,row in a_df.iterrows():
        print(row)
        precond_df = portfolio.query('Country ==\''+ row['Country'] + '\' and Ticker==\'' + row['Ticker'] + '\'')
        precond_df['CreatedDate']= pd.to_datetime(precond_df['CreatedDate'])
        start_date_projection = precond_df['CreatedDate'].max()
        start_year = start_date_projection.year
        noOfYears = year - start_year
        noOfMonths = noOfYears * 12
        r = relativedelta(start_date_projection, last_date)
        #noOfMonths = r.months
        precond_df = precond_df.query('CreatedDate ==\'' + str(start_date_projection)+ '\'')
        precond_df=precond_df.filter(items=['Company','Country','Ticker','Quantity','CreatedDate','Stock_Price','Invested_Value'])
        
        #a_df_temp = a_df_temp.append(precond_df)
        previousMonthDate = start_date_projection
        another_temp = precond_df.query('CreatedDate ==\'' + str(previousMonthDate)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')
        prevStockPrice = another_temp['Stock_Price'].iloc[0]
        for month in range (1, noOfMonths):
            nextMonthDate = start_date_projection + relativedelta(months=+month)
            another_temp = a_df_temp.query('CreatedDate ==\'' + str(previousMonthDate)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')
            try:
                if month != 1:
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
                newStockPrice = prevStockPrice * (1 - calculate_SAD(row['Latitude'],str(previousMonthDate)) - (corr/12) - discount_rate + growth_rate)
            else:
                newStockPrice = prevStockPrice * (1 - discount_rate + growth_rate)
            a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':nextMonthDate,'Stock_Price':newStockPrice,'Invested_Value':row['Quantity'] * newStockPrice}, ignore_index=True)
            print(prevStockPrice)
            previousMonthDate = nextMonthDate
    print(a_df_temp)
    a_df_temp = a_df_temp.append(portfolio)
    a_df_temp.to_csv("projected_result_temp.csv")


def plot_projection( projection):
    print(projection)
    result_df = pd.DataFrame()
    projection_grouped = projection.groupby(['CreatedDate'])['Invested_Value'].sum()
    result_df = projection_grouped
      
    result_df.to_csv("result_df_grouped.csv")
    result_df = pd.read_csv("result_df_grouped.csv")
    #result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedMonth'] = result_df['CreatedDate'].dt.month
    result_df['CreatedYear'] = result_df['CreatedDate'].dt.year
    
    result_df.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df_grouped = result_df.groupby(['CreatedYear','CreatedMonth'])['Invested_Value'].sum()
    
    result_df_grouped.to_csv("result_df_grouped_1.csv")
    result_df_grouped = pd.read_csv("result_df_grouped_1.csv")
    result_df_grouped.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df_grouped['Created'] = result_df_grouped['CreatedYear'].astype(str) + ' : ' + result_df_grouped['CreatedMonth'].astype(str)
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot()
    #ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.plot(result_df_grouped.Created, result_df_grouped.Invested_Value)
    ax.set_ylabel("ROIC")
    ax.set_xlabel("Timeframe")
    #ax.set_xticks(rotation=45)
    ax.grid(True)
    fig.autofmt_xdate()
    plt.savefig('projection_plot.png',format='png')

corr_data = load_corr_data()
#corr_data.to_csv("corr_master.csv")
#print(corr_data)

climate_data = load_climate_data()
#climate_data.to_csv("climate_master.csv")
#print(climate_data)

#portfolio = load_portfolio('portfolio_sample_1')
portfolio = load_portfolio('portfolio_sample_2')
#print(portfolio)



#project_empty_dataset(portfolio, 2026)
#increase_temp_model(portfolio,corr_data,climate_data,2050)
increase_temp_model_SAD(portfolio,corr_data,climate_data,0.04,0.08,2025)

projection = pd.DataFrame()
projection = pd.read_csv('projected_result_temp.csv')

plot_projection(projection)



#calculate_SAD()


