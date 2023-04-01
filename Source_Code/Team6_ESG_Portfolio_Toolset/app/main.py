from flask import Flask, redirect, url_for, render_template, jsonify, request
import os
import pandas as pd
import numpy as np
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
import json
import requests
from configparser import ConfigParser
import urllib3
from dateutil import parser

basedir = os.path.abspath(os.path.dirname(__file__))

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
configur = ConfigParser()
print(configur.read(os.path.join(basedir, 'config.ini')))
apiurl = configur.get('API','baseurl')

@app.route('/')
def show():
   app.logger.info('this is the root folder')
   #app.logger.info()
   #app.logger.info('testing info log')
   #res = requests.get(apiurl + 'portfolio/get/portfolio_sample_1')
   return 'Portfolio'

@app.route('/model/parameters')
def show_model_parameters():
    app.logger.info('show model parameters')
    return render_template("modelparameters.html")

@app.route('/model', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
       app.logger.info('run model started')
       grate = request.form.get("grate")
       drate = request.form.get("drate")
       portfolio = request.form.get("portf")
       fyear = request.form.get("fyear")
       app.logger.info("You selected : "+grate  + " " + drate + " " + portfolio+ " " + fyear)
       dict = {}
       #modelrun/portfolios/portfolio_sample_1
       inp = {}
       inp['discount_rate'] = float(drate)
       inp['growth_rate'] = float(grate)
       inp['forecast_year'] = int(fyear)
       http = urllib3.PoolManager()
       req = http.request('POST',url = apiurl + 'modelrun/portfolios/{0}'.format(portfolio),
                          headers={'Content-Type': 'application/json'},body=json.dumps(inp))
 
       response = json.loads(req.data)
       dict['message'] = response['ModelRan']
       dict['file'] = portfolio
       return render_template('model_result.html', result=dict,title='ESG Portfolio toolkit')
    portfoliolist = get_portfolio_list()
    app.logger.info('run model completed')
    return render_template("model.html",portfolio_list=portfoliolist)

def show_portfolio_plot(portfolio_grouped,portfolio_grouped_ESG):
    app.logger.info('generating the plot')
    img = BytesIO()
    fig, ax = plt.subplots(nrows=2, ncols=1)
    plt.title = "Invested Amount Vs ESG Score"
    #df['day'] = df['day'].dt.strftime('%Y-%m-%d')
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate']).dt.strftime('%m/%d/%Y')
    portfolio_grouped_ESG['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate']).dt.strftime('%m/%d/%Y')
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

def portfolio_returns_calculation(portfolio_grouped,benchmark):
    app.logger.info('portfolio returns calculation method entered')
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

def get_portfolio_list():
    res = requests.get(apiurl + 'portfoliomanagement/portfolios')
    print(res.text)
    portlist = json.loads(res.text)
    return portlist


@app.route('/portfolio/modify', methods =["GET", "POST"])
def show_portfolio_modifymain():
    app.logger.info('show portfolio modify main entered')

    if request.method == "POST":
       grate = request.form.get("port_id")
       app.logger.info('portfolio id: ' + grate)
       modifyaction = request.form.get("rdModify")
       app.logger.info('action: ' + modifyaction)
       plot_url1, plot_url2,portfolio_data, benchmark_data, data_portfolio = show_portfolio_data(grate)
       stocks = pd.DataFrame(portfolio_data)['Ticker']
       if modifyaction == 'delete':
           return render_template('modifyportfolio.html',stock_list=stocks, portfolio_id = grate,title='ESG Portfolio')
       else:
           basedir = os.path.abspath(os.path.dirname(__file__))
           portfolio_file = os.path.join(basedir, 'data/portfolio_sample_master.csv')
           portfoliolist = pd.read_csv(portfolio_file)
           portfolio_list=portfoliolist['Ticker'].unique()
           return render_template('addportfolio.html',stock_list=portfolio_list, portfolio_id = grate,title='ESG Portfolio')
    portfoliolist = get_portfolio_list()
    return render_template('modifyportfoliomain.html',portfolio_list=portfoliolist,title='ESG Portfolio Toolkit')


def delete_portfolio(name,to,ticker):
    app.logger.info('delete stock from portfolio entered')

    inp = {}
    inp['portfolio_newname'] = to
    inp['tickeradded'] = ''
    inp['tickerremoved'] = ticker
    http = urllib3.PoolManager()
    req = http.request('POST',url = apiurl + 'portfoliomanagement/portfolios/{0}'.format(name),
                        headers={'Content-Type': 'application/json'},body=json.dumps(inp))
 
    response = json.loads(req.data)

    app.logger.info('Successfully deleted the stock {0} from portfolio {1}'.format(ticker,to))
    return('Successfully deleted the stock {0} from portfolio {1}'.format(ticker,to))

def _add_to_portfolio(name,to,ticker):

    inp = {}
    inp['portfolio_newname'] = to
    inp['tickeradded'] = ticker
    inp['tickerremoved'] = ''
    http = urllib3.PoolManager()
    req = http.request('POST',url = apiurl + 'portfoliomanagement/portfolios/{0}'.format(name),
                        headers={'Content-Type': 'application/json'},body=json.dumps(inp))
 
    response = json.loads(req.data)

    if response['alreadyexists'] == False:
        msg = 'Stock {0} added to the portfolio {1} successfully!!'.format(ticker,to)
    else:
        msg = 'Stock already exists in the portfolio!!'
    app.logger.info(msg)
    return msg

@app.route('/portfolio/add',methods =["GET", "POST"])
def add_to_portfolio():
    if request.method == "POST":
        portfolioname = request.form.get("portfolio_id")
        toportfolioname = request.form.get("toportfolio")
        ticker = request.form.get("add_stock_id")
        return render_template('addresult.html',result=_add_to_portfolio(portfolioname,toportfolioname,ticker))
    
@app.route('/portfolio/delete', methods =["GET", "POST"])
def delete_from_portfolio():
    if request.method == "POST":
        portfolioname = request.form.get("portfolio_id")
        toportfolioname = request.form.get("toportfolio")
        ticker = request.form.get("delete_stock_id")
        return render_template('deleteresult.html',result=delete_portfolio(portfolioname,toportfolioname,ticker))

@app.route('/portfolio/main', methods =["GET", "POST"])
def show_portfolio_main():
    app.logger.info('show portfolio main entered')
    if request.method == "POST":
       grate = request.form.get("port_id")
       drate = request.form.get("counter_id")
       plot_url1, plot_url2,portfolio_data, benchmark_data, data_portfolio = show_portfolio_data(grate)
       return render_template('portfolio.html', portfolio_data=portfolio_data,benchmark_data=benchmark_data,plot_url1=plot_url1,data_portfolio=data_portfolio,plot_url2=plot_url2,title='ESG Portfolio')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfoliolist = get_portfolio_list()
    return render_template('portfoliomain.html',portfolio_list=portfoliolist,title='ESG Portfolio Toolkit')

@app.route('/projection/main', methods =["GET", "POST"])
def show_projection_main():
    app.logger.info('show projection main entered')
    if request.method == "POST":
       grate = request.form.get("port_id")
       
       plot_url, projection_data = show_projection_data(grate)

       return render_template('projection.html', projection_data=projection_data,plot_url=plot_url,portfolio_name=grate,title='Climate Data Projection')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfoliolist = get_portfolio_list()
    return render_template('projectionmain.html',portfolio_list=portfoliolist,title='ESG Portfolio Toolkit')

@app.route('/portfolio/<name>')
def show_portfolio(name):  
   app.logger.info('show portfolio entered')
   app.logger.info(name)
   plot_url1, plot_url2,portfolio_data, benchmark_data, data_portfolio = show_portfolio_data(name)
   return render_template('portfolio.html', portfolio_data=portfolio_data,benchmark_data=benchmark_data,plot_url1=plot_url1,data_portfolio=data_portfolio,plot_url2=plot_url2,title='ESG Portfolio')

def show_portfolio_data(name):
   app.logger.info('show portfolio data entered')
    
   res = requests.get(apiurl + 'portfoliomanagement/portfolios/{0}'.format(name))
   print(res.text)
   portlist = json.loads(res.text)
   data = portlist['portfolio_stocks']
   data_benchmark = portlist['benchmark_summary']
   data_portfolio=portlist['portfolio_summary']
   plot_data=pd.DataFrame(portlist['plot_data'])
   plot_data_esg=pd.DataFrame(portlist['plot_data_esg'])
   returns_data=pd.DataFrame(portlist['returns_data'])
   benchmark=pd.DataFrame(portlist['benchmark'])
   plot_url1 = show_portfolio_plot(plot_data,plot_data_esg)
   plot_url2=portfolio_returns_calculation(returns_data,benchmark)
   #return render_template('portfolio.html', portfolio_data=data.to_dict(orient='records'),benchmark_data=data_benchmark.to_dict(orient='records'),plot_url1=plot_url,data_portfolio=data_portfolio.to_dict(orient='records'),plot_url2=portfolio_returns_calculation(name),title='ESG Portfolio')
   return plot_url1,plot_url2, data, data_benchmark, data_portfolio


   #return jsonify(WORDS)
    #return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/projection/<name>')
def show_projection(name):
    app.logger.info('show projection entered')
    plot_url, projection_data = show_projection_data(name)
    app.logger.info('projecton data loaded')
    return render_template('projection.html', projection_data=projection_data,plot_url=plot_url,title='Climate Data Projection')

@app.route('/projection/compare', methods =["GET", "POST"])
def compare_projection():
    app.logger.info('compare projection entered')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfoliolist = get_portfolio_list()
    app.logger.info('portfolio list loaded')
    if request.method == "POST":
       port1 = request.form.get("port1_id")
       port2 = request.form.get("port2_id")
       plot_url1, projection_data1 = show_projection_data(port1)
       app.logger.info('projection loaded for ' + port1) 
       plot_url2, projection_data2 = show_projection_data(port2)
       app.logger.info('projection loaded for ' + port2)
       return render_template('compareprojection.html',port1 = port1, port2=port2,portfolio_list=portfoliolist, projection_data1=projection_data1,plot_url1=plot_url1,projection_data2=projection_data2,plot_url2=plot_url2,title='Climate Data Projection')
    return render_template('compareprojection.html',portfolio_list=portfoliolist,title='Climate Data Projection')


def show_projection_data(name):
    res = requests.get(apiurl + 'projection/portfolios/{0}'.format(name))
    print(res.text)
    portlist = json.loads(res.text)
    result_df_grouped = pd.DataFrame(portlist['result_df_grouped'])
    pd_result = pd.DataFrame(portlist['pd_result'])
    date1 = parser.parse(portlist['final_date'])
    final_date = datetime(date1.year,date1.month,date1.day).date()
    #final_date = datetime.strptime(portlist['final_date'],'%a, %d %b %Y %H:%M:%S %Z%z')
    result_df_grouped['CreatedDate'] = pd.to_datetime(result_df_grouped['CreatedDate']).dt.date
    app.logger.info('coloring the plots based on history vs forecast')
    past = result_df_grouped['CreatedDate'] <= final_date
    future = result_df_grouped['CreatedDate'] >= final_date
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot()
    img = BytesIO()
    #ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.plot(result_df_grouped.CreatedDate[past], result_df_grouped.Invested_Value[past],color='blue')
    ax.plot(result_df_grouped.CreatedDate[future], result_df_grouped.Invested_Value_NoImpact[future],color='blue')
    ax.plot(result_df_grouped.CreatedDate[future], result_df_grouped.Invested_Value[future],color='crimson')
    ax.set_ylabel("ROIC")
    ax.set_xlabel("Timeframe")
    #ax.set_xticks(rotation=45)
    ax.grid(True)
    fig.autofmt_xdate()
    plt.savefig(img,format='png')
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url, pd_result.to_dict(orient='records')
    #return render_template('projection.html', projection_data=pd_result.to_dict(orient='records'),plot_url=plot_url,title='Climate Data Projection 2050')


if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)
