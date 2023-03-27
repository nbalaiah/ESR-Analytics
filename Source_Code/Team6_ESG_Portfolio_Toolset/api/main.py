from flask import Flask, redirect, url_for, render_template, jsonify, request
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import math
from dateutil.relativedelta import relativedelta
import matplotlib.dates as mdates
from datetime import date
from datetime import datetime
import random
from logging.config import dictConfig

app = Flask(__name__)

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

def show_portfolio_plot(name):
    app.logger.info(name)
    app.logger.info('show portfolio plot method to generate portfolio data')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio = pd.read_csv(os.path.join(basedir,"data\\{0}.csv".format(name)))
    portfolio_grouped = portfolio.groupby(['Country','Company','Ticker','CreatedDate'])['Invested_Value'].agg("sum")
    #print(portfolio_grouped)
    #portfolio_grouped.to_csv("data\\portfolio_grouped.csv")
    portfolio_grouped = portfolio.groupby(['CreatedDate'])['Invested_Value'].agg("sum")

    portfolio_grouped_ESG = portfolio.groupby(['CreatedDate'])['ESGScore'].agg("mean")
    

    portfolio_grouped.to_csv(os.path.join(basedir,"data\\portfolio_grouped_stock_{0}.csv".format(name)))
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data\\portfolio_grouped_stock_{0}.csv".format(name)))
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    
    portfolio_grouped_ESG.to_csv(os.path.join(basedir,"data\\portfolio_grouped_esg_{0}.csv".format(name)))
    portfolio_grouped_ESG = pd.read_csv(os.path.join(basedir,"data\\portfolio_grouped_esg_{0}.csv".format(name)))
    portfolio_grouped_ESG['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped_ESG.sort_values(['CreatedDate'],inplace=True)
    app.logger.info('generating the plot')
    img = BytesIO()
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
    plt.savefig(img,format='png')
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return(plot_url)

def portfolio_returns_calculation(name):
    app.logger.info('portfolio returns calculation method entered')
    app.logger.info(name)
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data\\portfolio_grouped_stock_{0}.csv".format(name)))

    benchmark = pd.DataFrame()
    try:
        benchmark_file = os.path.join(basedir, 'data/benchmark_{0}.csv'.format(name))
        benchmark = pd.read_csv(benchmark_file)
    except:
        benchmark_file = os.path.join(basedir, 'data/benchmark.csv'.format(name))
        benchmark = pd.read_csv(benchmark_file)
    
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    portfolio_grouped['ROIC'] = portfolio_grouped['Invested_Value']
    app.logger.info('portfolio plot generation Benchmark Vs Portfolio')
    img = BytesIO()
    fig, ax = plt.subplots(nrows=2, ncols=1)
    
    ax[0].plot(portfolio_grouped['CreatedDate'], portfolio_grouped['ROIC'])
    plt.title = "MSCI USA ESG Select ETF Vs Portfolio"
    ax[0].set_ylabel("Portfolio")
    ax[0].set_xlabel("Timeframe")
    ax[0].tick_params(axis='x', rotation=45)

    ax[1].plot(benchmark['CreatedDate'], benchmark['Invested_Value'])
    
    ax[1].set_ylabel("Benchmark")
    ax[1].set_xlabel("Timeframe")
    ax[1].tick_params(axis='x', rotation=45)
    fig.autofmt_xdate()
    plt.savefig(img,format='png')
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return(plot_url)

@app.route('/')
def show():
   app.logger.info('this is the root folder')
   #app.logger.error('testing error log')
   #app.logger.info('testing info log')
   return 'Portfolio'

@app.route('/api/portfolio/get/<name>')
def show_portfolio_data(name):
   app.logger.info('show portfolio data entered')
   basedir = os.path.abspath(os.path.dirname(__file__))
   portfolio_file = os.path.join(basedir, 'data/' + name + '.csv')
   try:
       benchmark_file = os.path.join(basedir, 'data/benchmark_{0}.csv'.format(name))
       benchmark = pd.read_csv(benchmark_file)
   except:
       benchmark_file = os.path.join(basedir, 'data/benchmark.csv'.format(name))
       benchmark = pd.read_csv(benchmark_file)
   app.logger.info('benchmark data loaded')
   portfolio = pd.read_csv(portfolio_file)
   #benchmark = pd.read_csv(benchmark_file)
   portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
   benchmark['CreatedDate']= pd.to_datetime(benchmark['CreatedDate'])
   maxDate = portfolio['CreatedDate'].max()
   minDate = portfolio['CreatedDate'].min()
   tickers = portfolio['Ticker'].unique()
   data = pd.DataFrame()
   data_benchmark = pd.DataFrame()
   data_portfolio = pd.DataFrame()
   app.logger.info('portfolio data loaded')
   invested_value_bench = benchmark.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].iloc[0]
   current_value_bench = benchmark.query('CreatedDate ==\'' + str(maxDate) + '\'')['Invested_Value'].iloc[0]
   data_benchmark = data_benchmark.append({'Invested_Value':invested_value_bench,'Current_Value':current_value_bench},ignore_index=True)

   invested_value_port = portfolio.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].sum()
   current_value_port = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\'')['Invested_Value'].sum()
   data_portfolio = data_portfolio.append({'Invested_Value':invested_value_port,'Current_Value':current_value_port},ignore_index=True)

   for ticker in tickers:
        invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        current_value = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        climate_value = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['Climate'].iloc[0]
        data = data.append({'Ticker':ticker,'Invested_Value': invested_value,'Current_Value':current_value,'Climate': climate_value},ignore_index=True)

   plot_url1 = show_portfolio_plot(name)
   plot_url2=portfolio_returns_calculation(name)
   WORDS = {
       'plot_url1': plot_url1,
       'plot_url2':plot_url2,
       'data':data.to_dict(orient='records'),
       'data_benchmark':data_benchmark.to_dict(orient='records'),
       'data_portfolio':data_portfolio.to_dict(orient='records')
   }
   #return render_template('portfolio.html', portfolio_data=data.to_dict(orient='records'),benchmark_data=data_benchmark.to_dict(orient='records'),plot_url1=plot_url,data_portfolio=data_portfolio.to_dict(orient='records'),plot_url2=portfolio_returns_calculation(name),title='ESG Portfolio')
   #return plot_url1,plot_url2, data.to_dict(orient='records'), data_benchmark.to_dict(orient='records'), data_portfolio.to_dict(orient='records')


   return jsonify(WORDS)

if __name__ == '__main__':
    #app.debug = True
    app.run(port=8082)
    #app.run(debug = True)