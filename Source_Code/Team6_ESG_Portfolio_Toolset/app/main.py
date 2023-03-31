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
       dict['message'] = increase_temp_model_SAD(portfolio,float(drate),float(grate),int(fyear))
       dict['file'] = portfolio
       return render_template('model_result.html', result=dict,title='ESG Portfolio toolkit')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    app.logger.info('run model completed')
    return render_template("model.html",portfolio_list=portfoliolist.to_dict(orient='records'))

def show_portfolio_plot(name):
    app.logger.info(name)
    app.logger.info('show portfolio plot method to generate portfolio data')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio = pd.read_csv(os.path.join(basedir,"data/{0}.csv".format(name)))
    portfolio_grouped = portfolio.groupby(['Country','Company','Ticker','CreatedDate'])['Invested_Value'].agg("sum")
    #print(portfolio_grouped)
    #portfolio_grouped.to_csv("data/portfolio_grouped.csv")
    portfolio_grouped = portfolio.groupby(['CreatedDate'])['Invested_Value'].agg("sum")

    portfolio_grouped_ESG = portfolio.groupby(['CreatedDate'])['ESGScore'].agg("mean")
    

    portfolio_grouped.to_csv(os.path.join(basedir,"data/portfolio_grouped_stock_{0}.csv".format(name)))
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data/portfolio_grouped_stock_{0}.csv".format(name)))
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    
    portfolio_grouped_ESG.to_csv(os.path.join(basedir,"data/portfolio_grouped_esg_{0}.csv".format(name)))
    portfolio_grouped_ESG = pd.read_csv(os.path.join(basedir,"data/portfolio_grouped_esg_{0}.csv".format(name)))
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
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data/portfolio_grouped_stock_{0}.csv".format(name)))

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

    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    return render_template('modifyportfoliomain.html',portfolio_list=portfoliolist.to_dict(orient='records'),title='ESG Portfolio Toolkit')

def add_to_portfolio_list(name):
    app.logger.info('add to portfolio list entered')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    res = portfoliolist.query('Name ==\'' + name + '\'')
    if res.empty == True:
        portfoliolist = portfoliolist.append({'Name': name},ignore_index=True)
        portfoliolist.to_csv(portfolio_file)
        app.logger.info('portfolio added successfully to the master list')

def recalculate_benchmark(name, portfoliovalue):
    basedir = os.path.abspath(os.path.dirname(__file__))
    benchmark_file = os.path.join(basedir, 'data/{0}.csv'.format(name))
    benchmark = pd.read_csv(benchmark_file)
    minDate = benchmark['CreatedDate'].min()
    stock_price = benchmark.query('CreatedDate ==\'' + str(minDate) + '\'')['Stock_Price'].iloc[0]
    qty = math.floor(portfoliovalue/stock_price)
    benchmark['Invested_Value'] = benchmark['Stock_Price'] * qty
    benchmark.to_csv(benchmark_file)

def delete_portfolio(name,to,ticker):
    app.logger.info('delete stock from portfolio entered')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(name))
    to_portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(to))
    portfolio = pd.read_csv(portfolio_file)
    portfolio['Ticker'].str.replace(' ','')
    portfolio.drop(portfolio[portfolio['Ticker'].str.contains(ticker.replace(' ',''))].index, inplace = True)
    minDate = portfolio['CreatedDate'].min()
    invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].sum()
    #recalculate_benchmark('benchmark_{0}'.format(name),invested_value)
    add_to_portfolio_list(to)
    portfolio.to_csv(to_portfolio_file)
    app.logger.info('Successfully deleted the stock {0} from portfolio {1}'.format(ticker,to))
    return('Successfully deleted the stock {0} from portfolio {1}'.format(ticker,to))

def _add_to_portfolio(name,to,ticker):
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(name))
    portfolio = pd.read_csv(portfolio_file)
    portfolio_master = pd.read_csv(os.path.join(basedir,'data/{0}.csv'.format('portfolio_sample_master')))
    existsData = portfolio.query('Ticker ==\'' + ticker + '\'')
    if existsData.empty == True:
        portfolio = portfolio.append(portfolio_master.query('Ticker ==\'' + ticker + '\''))
        msg = 'Stock {0} added to the portfolio {1} successfully!!'.format(ticker,to)
    else:
        msg = 'Stock already exists in the portfolio!!'
    portfolio_to_file = os.path.join(basedir, 'data/{0}.csv'.format(to))
    portfolio.to_csv(portfolio_to_file)
    add_to_portfolio_list(to)
    #minDate = portfolio['CreatedDate'].min()
    #invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].sum()
    #recalculate_benchmark('benchmark_{0}'.format(name),invested_value)
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
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    return render_template('portfoliomain.html',portfolio_list=portfoliolist.to_dict(orient='records'),title='ESG Portfolio Toolkit')

@app.route('/projection/main', methods =["GET", "POST"])
def show_projection_main():
    app.logger.info('show projection main entered')
    if request.method == "POST":
       grate = request.form.get("port_id")
       plot_url, projection_data = show_projection_data(grate)

       return render_template('projection.html', projection_data=projection_data,plot_url=plot_url,portfolio_name=grate,title='Climate Data Projection')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    return render_template('projectionmain.html',portfolio_list=portfoliolist.to_dict(orient='records'),title='ESG Portfolio Toolkit')

@app.route('/portfolio/<name>')
def show_portfolio(name):  
   app.logger.info('show portfolio entered')
   app.logger.info(name)
   plot_url1, plot_url2,portfolio_data, benchmark_data, data_portfolio = show_portfolio_data(name)
   return render_template('portfolio.html', portfolio_data=portfolio_data,benchmark_data=benchmark_data,plot_url1=plot_url1,data_portfolio=data_portfolio,plot_url2=plot_url2,title='ESG Portfolio')

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
        ESGScore = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['ESGScore'].iloc[0]
        Up = 1 if invested_value > current_value else 0
        data = data.append({'Ticker':ticker,'Invested_Value': invested_value,'Current_Value':current_value,'Climate': climate_value,'ESGScore': ESGScore,'Up': Up},ignore_index=True)

   plot_url1 = show_portfolio_plot(name)
   plot_url2=portfolio_returns_calculation(name)
   #return render_template('portfolio.html', portfolio_data=data.to_dict(orient='records'),benchmark_data=data_benchmark.to_dict(orient='records'),plot_url1=plot_url,data_portfolio=data_portfolio.to_dict(orient='records'),plot_url2=portfolio_returns_calculation(name),title='ESG Portfolio')
   return plot_url1,plot_url2, data.to_dict(orient='records'), data_benchmark.to_dict(orient='records'), data_portfolio.to_dict(orient='records')


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
    portfolio_file = os.path.join(basedir, 'data/portfolio_list.csv')
    portfoliolist = pd.read_csv(portfolio_file)
    app.logger.info('portfolio list loaded')
    if request.method == "POST":
       port1 = request.form.get("port1_id")
       port2 = request.form.get("port2_id")
       plot_url1, projection_data1 = show_projection_data(port1)
       app.logger.info('projection loaded for ' + port1) 
       plot_url2, projection_data2 = show_projection_data(port2)
       app.logger.info('projection loaded for ' + port2)
       return render_template('compareprojection.html',port1 = port1, port2=port2,portfolio_list=portfoliolist.to_dict(orient='records'), projection_data1=projection_data1,plot_url1=plot_url1,projection_data2=projection_data2,plot_url2=plot_url2,title='Climate Data Projection')
    return render_template('compareprojection.html',portfolio_list=portfoliolist.to_dict(orient='records'),title='Climate Data Projection')


def show_projection_data(name):
    pd_result = pd.DataFrame()
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.logger.info('projection result loaded')
    projection_file = os.path.join(basedir, 'data/projected_result_{0}.csv'.format(name))
    portfolio_file = os.path.join(basedir, 'data/{0}.csv'.format(name))
    portfolio = pd.read_csv(portfolio_file)
    app.logger.info('portfolio data loaded')
    portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
    final_date = portfolio['CreatedDate'].max()
    year, month, day = str(final_date).split('-')
    projection = pd.read_csv(projection_file)
    projection['CreatedDate']= pd.to_datetime(projection['CreatedDate'])
    maxDate = projection['CreatedDate'].max()
    minDate = projection['CreatedDate'].min()
    pd_result_2050 = projection.query('CreatedDate ==\''+str(maxDate)+'\'')
    pd_result_invested = projection.query('CreatedDate ==\''+str(minDate)+'\'')
    app.logger.info('iterating through projection result')
    for index, row in pd_result_2050.iterrows():       
        invested_amount = projection.query('CreatedDate ==\''+str(minDate)+'\' and Ticker ==\'' + row['Ticker']+ '\'')['Invested_Value'].iloc[0]
        invested_amount_noimpact = projection.query('CreatedDate ==\''+str(minDate)+'\' and Ticker ==\'' + row['Ticker']+ '\'')['Invested_Value_NoImpact'].iloc[0]
        print(invested_amount)
        pd_result = pd_result.append({'Ticker':row['Ticker'],'Invested_Value': invested_amount,'Invested_Value_NoImpact': invested_amount_noimpact,'_2050_Value':row['Invested_Value'],'Company':row['Company'],'Country':row['Country']},ignore_index=True)
    #return pd_result.to_html()
    app.logger.info('Grouping invested value based on date')
    result_df = pd.DataFrame()
    projection['Invested_Value_NoImpact'].fillna(0)
    projection_grouped = projection.groupby(['CreatedDate']).agg(
     Invested_Value = ('Invested_Value','sum'),
     Invested_Value_NoImpact = ('Invested_Value_NoImpact','sum'),
     ).reset_index()
    result_df = projection_grouped
      
    result_df.to_csv(os.path.join(basedir,"data/result_df_grouped_{0}.csv".format(name)))
    result_df = pd.read_csv(os.path.join(basedir,"data/result_df_grouped_{0}.csv".format(name)))
    #result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    #result_df['CreatedMonth'] = result_df['CreatedDate'].dt.month
    #result_df['CreatedYear'] = result_df['CreatedDate'].dt.year
    
    #result_df.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df.sort_values(['CreatedDate'],inplace=True)
    #result_df_grouped = result_df.groupby(['CreatedDate'])['Invested_Value'].sum()
    
    result_df_grouped = result_df.groupby(['CreatedDate']).agg(
     Invested_Value = ('Invested_Value','sum'),
     Invested_Value_NoImpact = ('Invested_Value_NoImpact','sum'),
     ).reset_index()

    result_df_grouped.to_csv(os.path.join(basedir,"data/result_df_grouped_1_{0}.csv".format(name)))
    result_df_grouped = pd.read_csv(os.path.join(basedir,"data/result_df_grouped_1_{0}.csv".format(name)))
    result_df_grouped['CreatedDate']= pd.to_datetime(result_df_grouped['CreatedDate'])
    #result_df_grouped['Created'] = result_df_grouped['CreatedYear'].astype(str) + ' : ' + result_df_grouped['CreatedMonth'].astype(str)
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


def calculate_SAD(latitude, CreatedDate):
    app.logger.info('SAD calculation entered')
    latitude = float(latitude)
    year, month, day = CreatedDate.split('-')
    day=day[:2]
    inside = 2 * 3.14 / 365 * (float(day) - 80.25)
    sun_inclination_angle = 0.4102 * math.sin(inside)
    Ht = 24 - (7.72 * (- math.tan(2 * 3.14 * latitude / 360) * math.tan(sun_inclination_angle)))
    SAD = Ht - 12
    #print(SAD/1000)
    return(SAD/(24*100))

def increase_temp_model_SAD(portfolioname,discount_rate,growth_rate, year):
    app.logger.info('model calculation entered')
    vol_list = [-1, 0, 1 ]
    app.logger.info('vol randomess loaded')
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio = pd.DataFrame()
    portfolio_file = os.path.join(basedir, 'data/' + portfolioname + '.csv')
    portfolio = pd.read_csv(portfolio_file)
    app.logger.info('climate data loaded')
    climate_file = os.path.join(basedir, 'data/climate_master.csv')
    climate_data = pd.DataFrame()
    climate_data = pd.read_csv(climate_file)
    app.logger.info('correlation data loaded')
    corr_file = os.path.join(basedir, 'data/corr_master.csv')
    corr_data = pd.DataFrame()
    corr_q = pd.read_csv(corr_file)
    corr_q = corr_q.query('Stock_Price != 1')
    corr_q.update(corr_q.fillna(0))
    corr_data = corr_q

    

    output_file = os.path.join(basedir, "data/projected_result_{0}.csv".format(portfolioname))

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
    app.logger.info('iterating through the list of stocks to forecast')
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
        app.logger.info('the no of months to forecast ' + str(noOfMonths))
        #a_df_temp = a_df_temp.append(precond_df)
        previousMonthDate = start_date_projection
        another_temp = precond_df.query('CreatedDate ==\'' + str(previousMonthDate)+ '\' and Ticker ==\'' +row['Ticker']+ '\'')

        app.logger.info('historic volatiltiy of the stock is calculated')
        TRADING_DAYS = 252
        returns = np.log(another_temp['Stock_Price']/another_temp['Stock_Price'].shift(1))
        returns.fillna(0, inplace=True)
        volatility = returns.rolling(window=TRADING_DAYS).std()*np.sqrt(TRADING_DAYS)
        vol_val = np.array(volatility).mean()
        if math.isnan(vol_val):
            vol_val = (0.10 * 22)/252
        
        prevStockPrice = another_temp['Stock_Price'].iloc[0]
        prevStockPrice_noimpact = prevStockPrice
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
            app.logger.info('get the previous stock value')
            query_fossil = climate_data.query('Ticker ==\'' + row['Ticker'] + '\'')
            print(query_fossil)
            vol = random.choice(vol_list)
            app.logger.info('calculate the new stock value')
            if query_fossil.empty == False and query_fossil['Ticker'].iloc[0] == row['Ticker']:
                query_corr= corr_data.query('Country ==\'' + row['Country']+ '\'')
                query_corr = query_corr[query_corr['Measure'].str.contains("Fossil")]
                if query_corr.empty == True:
                    corr = 0
                else:
                    corr = query_corr['Stock_Price'].mean()
                    #if isinstance(corr, pd.Series):
                     #   corr = corr['Stock_Price'].mean()
                newStockPrice = prevStockPrice * (1 - calculate_SAD(row['Latitude'],str(previousMonthDate)) - (corr/12) - discount_rate + (vol * vol_val) + growth_rate)
            else:
                newStockPrice = prevStockPrice * (1 - discount_rate + (vol * vol_val) + growth_rate)
            
            newStockPrice_noimpact = prevStockPrice_noimpact * (1 - discount_rate + (vol * vol_val) + growth_rate)
            prevStockPrice_noimpact = newStockPrice_noimpact
            a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':nextMonthDate,'Stock_Price':newStockPrice,'Invested_Value':row['Quantity'] * newStockPrice,'Stock_Price_NoImpact':newStockPrice_noimpact,'Invested_Value_NoImpact':row['Quantity'] * newStockPrice_noimpact}, ignore_index=True)
            print(prevStockPrice)
            app.logger.info('update the new stock value and continue the loop')
            previousMonthDate = nextMonthDate
    print(a_df_temp)
    a_df_temp = a_df_temp.append(portfolio)
    a_df_temp['Stock_Price_NoImpact'] = a_df_temp.apply(lambda x: x['Stock_Price'] if math.isnan(x['Stock_Price_NoImpact']) else x['Stock_Price_NoImpact'], axis=1)
    a_df_temp['Invested_Value_NoImpact'] = a_df_temp.apply(lambda x: x['Invested_Value'] if math.isnan(x['Invested_Value_NoImpact']) else x['Invested_Value_NoImpact'], axis=1)
    a_df_temp.to_csv(output_file)
    return 'Model ran successfully!!'

if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)
