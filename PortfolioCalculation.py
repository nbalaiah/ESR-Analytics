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
    portfolio_final.to_csv('data\\portfolio_sample_master.csv')
#build_portfolio()

def add_climate_data_to_portfolio():
    Dict = {}
    portfolio = pd.read_csv('data\portfolio_sample_master.csv')
    climate = pd.read_csv('data\\climate_master.csv')
    for index, row in portfolio.iterrows():
        climate_data_row = climate.query('Ticker ==\'' + row['Ticker'] + '\'')
        climate_data = climate_data_row['Climate'].unique()
        Dict[row['Ticker']] = ','.join(climate_data)
        print( Dict[row['Ticker']] )
        portfolio.at[index,'Climate']=','.join(climate_data)
    print(Dict)
    portfolio.to_csv('data\\portfolio_sample_master.csv')
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
    
    #benchmark.to_csv("data\\benchmark.csv") 

#build_benchmark()

def test_portfolio():
    portfolio = pd.read_csv('data\\portfolio_sample_1.csv')
    portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
    maxDate = portfolio['CreatedDate'].max()
    minDate = portfolio['CreatedDate'].min()
    tickers = portfolio['Ticker'].unique()
    data = pd.DataFrame()
    for ticker in tickers:
        invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        current_value = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        climate_value = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['Climate'].iloc[0]
        data = data.append({'Ticker':ticker,'Invested_Value': invested_value,'Current_Value':current_value,'Climate': climate_value},ignore_index=True)
#test_portfolio()

def add_country_data_to_portfolio():
    Dict = {}
    portfolio = pd.read_csv('data\\portfolio_sample_master.csv')
    climate = pd.read_csv('data\\companies_master.csv')
    for index, row in portfolio.iterrows():
        data_row = climate.query('Ticker ==\'' + row['Ticker'] + '\'')
        country_data = data_row['Country'].unique()
        company_data = data_row['Company'].unique()
        portfolio.at[index,'Country']=','.join(country_data)
        portfolio.at[index,'Company']=','.join(company_data)
 
    portfolio.to_csv('data\\portfolio_sample_master.csv')

#add_country_data_to_portfolio()

def recalculate_benchmark(name, portfoliovalue):
    benchmark = pd.read_csv('data\\{0}.csv'.format(name))
    minDate = benchmark['CreatedDate'].min()
    stock_price = benchmark.query('CreatedDate ==\'' + str(minDate) + '\'')['Stock_Price'].iloc[0]
    qty = math.floor(portfoliovalue/stock_price)
    benchmark['Invested_Value'] = benchmark['Stock_Price'] * qty
    benchmark.to_csv('data\\{0}.csv'.format(name))

def delete_portfolio(name,ticker):
    portfolio = pd.read_csv('data\\{0}.csv'.format(name))
    portfolio.drop(portfolio[portfolio['Ticker'].str.contains(ticker)].index, inplace = True)
    minDate = portfolio['CreatedDate'].min()
    invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].sum()
    recalculate_benchmark('benchmark_{0}'.format(name),invested_value)
    portfolio.to_csv('data\\{0}.csv'.format(name))

#delete_portfolio('portfolio_sample_delete_test','STNE')

def add_to_portfolio(name,ticker):
    portfolio = pd.read_csv('data\\{0}.csv'.format(name))
    portfolio_master = pd.read_csv('data\\{0}.csv'.format('portfolio_sample_master'))
    existsData = portfolio.query('Ticker ==\'' + ticker + '\'')
    if existsData.empty == True:
        portfolio = portfolio.append(portfolio_master.query('Ticker ==\'' + ticker + '\''))
        msg = 'Stock added to the portfolio successfully!!'
    else:
        msg = 'Stock already exists in the portfolio!!'
    portfolio.to_csv('data\\{0}.csv'.format(name))
    minDate = portfolio['CreatedDate'].min()
    invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].sum()
    recalculate_benchmark('benchmark_{0}'.format(name),invested_value)
    return msg

#build_portfolio()
#add_climate_data_to_portfolio()
#add_country_data_to_portfolio()
delete_portfolio('portfolio_sample_delete_test','BDL')
msg = add_to_portfolio('portfolio_sample_delete_test','BDL')
print(msg)