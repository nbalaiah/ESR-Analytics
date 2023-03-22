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
from random import sample
import math

def calculate_portfolio():
    portfolio = pd.read_csv("data\\portfolio_1.csv")
    portfolio_grouped = portfolio.groupby(['Country','Company','Ticker','CreatedDate'])['Invested_Value'].agg("sum")
    #print(portfolio_grouped)
    #portfolio_grouped.to_csv("data\\portfolio_grouped.csv")
    portfolio_grouped = portfolio.groupby(['CreatedDate'])['Invested_Value'].agg("sum")

    portfolio_grouped_ESG = portfolio.groupby(['CreatedDate'])['ESGScore'].agg("mean")
    

    portfolio_grouped.to_csv("data\\portfolio_grouped_stock.csv")
    portfolio_grouped = pd.read_csv("data\\portfolio_grouped_stock.csv")
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    
    portfolio_grouped_ESG.to_csv("data\\portfolio_grouped_esg.csv")
    portfolio_grouped_ESG = pd.read_csv("data\\portfolio_grouped_esg.csv")
    portfolio_grouped_ESG['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped_ESG.sort_values(['CreatedDate'],inplace=True)

    fig, ax = plt.subplots(nrows=2, ncols=1)
    plt.title = "Invested Amount Vs ESG Score"
    ax[0].plot(portfolio_grouped.CreatedDate, portfolio_grouped.Invested_Value)
    ax[1].plot(portfolio_grouped_ESG.CreatedDate, portfolio_grouped_ESG.ESGScore)
    ax[0].set_ylabel("Invested Value")
    ax[0].set_xlabel("Timeframe")
    ax[0].tick_params(axis='x', rotation=45)

    ax[1].set_ylabel("Avg ESG Score")
    ax[1].set_xlabel("Timeframe")
    ax[1].tick_params(axis='x', rotation=45)
    fig.autofmt_xdate()
    fig.savefig('portfolio_plot.png',format='png')

#calculate_portfolio()

def Get_Yahoo_Data(dateStr,stocks):
    testeddate = dateStr
    month, day, year = testeddate.split('/')
    testeddate = '-'.join([year, month, day])
    d = int(day)
    d = d + 1
    toDate = '-'.join([year, month, str(d)])
    for r in stocks.split(','):
        data = yf.download(r, start=testeddate, end=toDate,interval = "1d")
        #print(r)
        #print(toDate)
        if (data.count().sum() > 0):
            return r, data
    return r, data

def portfolio_returns_calculation():
    portfolio_grouped = pd.read_csv("data\\portfolio_grouped_stock.csv")
    invested_capital = 208274234
    benchmark_qty = 3435451.282
    colDates = portfolio_grouped['CreatedDate'].unique()
    benchmark = pd.DataFrame()
    for col in colDates:
        r, data = Get_Yahoo_Data(col,'SUSA')    
        if (data.empty == False and data['Close'].empty == False):
            #row['Stock_Price'] = data.iloc[0][1]      
            benchmark = benchmark.append([[col,data.iloc[0][1],benchmark_qty * data.iloc[0][1],benchmark_qty * data.iloc[0][1] / invested_capital]])
    benchmark[0] = pd.to_datetime(benchmark[0])
    benchmark.sort_values([0],inplace=True)
    benchmark.to_csv("data\\benchmark.csv") 
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    portfolio_grouped['ROIC'] = portfolio_grouped['Invested_Value'] / invested_capital

    fig, ax = plt.subplots(nrows=2, ncols=1)
    
    ax[0].plot(portfolio_grouped.CreatedDate, portfolio_grouped.ROIC)
    plt.title = "MSCI USA ESG Select ETF Vs Portfolio"
    ax[0].set_ylabel("ROIC")
    ax[0].set_xlabel("Timeframe")
    ax[0].tick_params(axis='x', rotation=45)

    ax[1].plot(benchmark[0], benchmark[3])
    
    ax[1].set_ylabel("Benchmark")
    ax[1].set_xlabel("Timeframe")
    ax[1].tick_params(axis='x', rotation=45)
    fig.autofmt_xdate()
    fig.savefig('portfolio_return.png',format='png')

#portfolio_returns_calculation()

def portfolio_sampling():
    portfolio = pd.read_csv("data\\portfolio.csv")
    tickers = portfolio['Ticker'].unique()
    portfolio_1 = sample(sorted(tickers),50)
    print(portfolio_1)
    portfolio_1_pd = pd.DataFrame();
    for ticker in portfolio_1:
        rows = portfolio.query('Ticker ==\'' + ticker + '\'')
        portfolio_1_pd = portfolio_1_pd.append(rows)
    #portfolio_1_pd.to_csv("data\\portfolio_3.csv")
    return portfolio_1, portfolio
#portfolio_sampling()

def build_portfolio(): 
    portfolio_sample, portfolio = portfolio_sampling()
    portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
    portfolio['month'] = pd.DatetimeIndex(portfolio['CreatedDate']).month
    portfolio['year'] = pd.DatetimeIndex(portfolio['CreatedDate']).year
    dates = pd.read_csv("data\\Dates.csv")
    portfolio_final = pd.DataFrame()
    for ticker in portfolio_sample:
        print(ticker)
        for index, date_ in dates.iterrows():
            print(date_)
            if (ticker !='Company'):
                r, stock_price = Get_Yahoo_Data(date_['CreatedDate'],ticker)
                month, day, year = date_['CreatedDate'].split('/')
                ESGScores = pd.DataFrame(portfolio.query('Ticker==\''+ticker +'\' and month==' + month + ' and year==' + year))
                print(ESGScores)
                if ESGScores.empty == False:
                    ESGScore = ESGScores['ESGScore'].iloc[0]
                else:
                    ESGScore = 0
                print(ESGScore)
                if (stock_price.empty == False and stock_price['Close'].empty == False):
                    stock = stock_price.iloc[0][1]
                else:
                    stock = 0
                portfolio_final = portfolio_final.append({'Ticker':ticker, 'CreatedDate':date_['CreatedDate'], 'Stock_Price':stock, 'ESGScore': ESGScore}, ignore_index=True)
    portfolio_final.to_csv('data\\portfolio_sample_1.csv')
#build_portfolio()

def add_climate_data_to_portfolio():
    Dict = {}
    portfolio = pd.read_csv('data\\portfolio_sample_1.csv')
    climate = pd.read_csv('data\\climate_master.csv')
    for index, row in portfolio.iterrows():
        climate_data_row = climate.query('Ticker ==\'' + row['Ticker'] + '\'')
        climate_data = climate_data_row['Climate'].unique()
        Dict[row['Ticker']] = ','.join(climate_data)
        print( Dict[row['Ticker']] )
        portfolio.at[index,'Climate']=','.join(climate_data)
    print(Dict)
    portfolio.to_csv('data\\portfolio_sample_1.csv')
#add_climate_data_to_portfolio()

def build_benchmark():
    #22987228.74
    #60.625
    benchmark_qty = math.floor(22987228.74 / 60.625)
    dates = pd.read_csv("data\\Dates.csv")
    benchmark = pd.DataFrame()
    for index, date_ in dates.iterrows():
        r, data = Get_Yahoo_Data(date_['CreatedDate'],'SUSA')    
        if (data.empty == False and data['Close'].empty == False):
            stock_price = data.iloc[0][1]      
            benchmark = benchmark.append({'Ticker':'SUSA','Stock_Price': stock_price,'Invested_Value:': stock_price * benchmark_qty,'CreatedDate': date_['CreatedDate']}, ignore_index=True)
    
    benchmark.to_csv("data\\benchmark.csv") 

build_benchmark()
