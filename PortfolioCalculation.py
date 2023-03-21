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

def calculate_portfolio():
    portfolio = pd.read_csv("data\\portfolio.csv")
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
    invested_capital = 395512270.1
    benchmark_qty = 6523913.734
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

portfolio_returns_calculation()