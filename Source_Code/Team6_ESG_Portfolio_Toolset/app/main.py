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

app = Flask(__name__)

@app.route('/')
def show():
   return 'Portfolio'

@app.route('/model', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
       grate = request.form.get("grate")
       drate = request.form.get("drate")
       portfolio = request.form.get("portf")
       fyear = request.form.get("fyear")
       #return "You selected : "+grate  + " " + drate + " " + portfolio+ " " + fyear
       dict = {}
       dict['message'] = increase_temp_model_SAD(portfolio,float(drate),float(grate),int(fyear))
       dict['file'] = portfolio
       return render_template('model_result.html', result=dict,title='ESG Portfolio toolkit')
    return render_template("model.html")

def show_portfolio_plot(name):
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
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio_grouped = pd.read_csv(os.path.join(basedir,"data\\portfolio_grouped_stock_{0}.csv".format(name)))

    benchmark = pd.DataFrame()
    benchmark_file = os.path.join(basedir, 'data/benchmark.csv')
    benchmark = pd.read_csv(benchmark_file)
    portfolio_grouped['CreatedDate']= pd.to_datetime(portfolio_grouped['CreatedDate'])
    portfolio_grouped.sort_values(['CreatedDate'],inplace=True)
    portfolio_grouped['ROIC'] = portfolio_grouped['Invested_Value']

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

@app.route('/portfolio/main', methods =["GET", "POST"])
def show_portfolio_main():
    if request.method == "POST":
       grate = request.form.get("port_id")
       drate = request.form.get("counter_id")
       plot_url1, plot_url2,portfolio_data, benchmark_data, data_portfolio = show_portfolio_data(grate)
       return render_template('portfolio.html', portfolio_data=portfolio_data,benchmark_data=benchmark_data,plot_url1=plot_url1,data_portfolio=data_portfolio,plot_url2=plot_url2,title='ESG Portfolio')
    return render_template('portfoliomain.html',title='ESG Portfolio Toolkit')

@app.route('/projection/main', methods =["GET", "POST"])
def show_projection_main():
    if request.method == "POST":
       grate = request.form.get("port_id")
       drate = request.form.get("counter_id")
       plot_url, projection_data = show_projection_data(grate)

       return render_template('projection.html', projection_data=projection_data,plot_url=plot_url,title='Climate Data Projection')

    return render_template('projectionmain.html',title='ESG Portfolio Toolkit')

@app.route('/portfolio/<name>')
def show_portfolio(name):  
   plot_url1, plot_url2,portfolio_data, benchmark_data, data_portfolio = show_portfolio_data(name)
   return render_template('portfolio.html', portfolio_data=portfolio_data,benchmark_data=benchmark_data,plot_url1=plot_url1,data_portfolio=data_portfolio,plot_url2=plot_url2,title='ESG Portfolio')

def show_portfolio_data(name):
   basedir = os.path.abspath(os.path.dirname(__file__))
   portfolio_file = os.path.join(basedir, 'data/' + name + '.csv')
   benchmark_file = os.path.join(basedir, 'data/benchmark.csv')
   portfolio = pd.read_csv(portfolio_file)
   benchmark = pd.read_csv(benchmark_file)
   portfolio['CreatedDate']= pd.to_datetime(portfolio['CreatedDate'])
   benchmark['CreatedDate']= pd.to_datetime(benchmark['CreatedDate'])
   maxDate = portfolio['CreatedDate'].max()
   minDate = portfolio['CreatedDate'].min()
   tickers = portfolio['Ticker'].unique()
   data = pd.DataFrame()
   data_benchmark = pd.DataFrame()
   data_portfolio = pd.DataFrame()

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
   #return render_template('portfolio.html', portfolio_data=data.to_dict(orient='records'),benchmark_data=data_benchmark.to_dict(orient='records'),plot_url1=plot_url,data_portfolio=data_portfolio.to_dict(orient='records'),plot_url2=portfolio_returns_calculation(name),title='ESG Portfolio')
   return plot_url1,plot_url2, data.to_dict(orient='records'), data_benchmark.to_dict(orient='records'), data_portfolio.to_dict(orient='records')


   #return jsonify(WORDS)
    #return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

@app.route('/projection/<name>')
def show_projection(name):
    plot_url, projection_data = show_projection_data(name)

    return render_template('projection.html', projection_data=projection_data,plot_url=plot_url,title='Climate Data Projection')

def show_projection_data(name):
    pd_result = pd.DataFrame()
    basedir = os.path.abspath(os.path.dirname(__file__))
    projection_file = os.path.join(basedir, 'data/projected_result_{0}.csv'.format(name))
    projection = pd.read_csv(projection_file)
    projection['CreatedDate']= pd.to_datetime(projection['CreatedDate'])
    maxDate = projection['CreatedDate'].max()
    minDate = projection['CreatedDate'].min()
    pd_result_2050 = projection.query('CreatedDate ==\''+str(maxDate)+'\'')
    pd_result_invested = projection.query('CreatedDate ==\''+str(minDate)+'\'')
    for index, row in pd_result_2050.iterrows():       
        invested_amount = projection.query('CreatedDate ==\''+str(minDate)+'\' and Ticker ==\'' + row['Ticker']+ '\'')['Invested_Value'].iloc[0]
        print(invested_amount)
        pd_result = pd_result.append({'Ticker':row['Ticker'],'Invested_Value': invested_amount,'_2050_Value':row['Invested_Value'],'Company':row['Company'],'Country':row['Country']},ignore_index=True)
    #return pd_result.to_html()

    result_df = pd.DataFrame()
    projection_grouped = projection.groupby(['CreatedDate'])['Invested_Value'].sum()
    result_df = projection_grouped
      
    result_df.to_csv(os.path.join(basedir,"data/result_df_grouped_{0}.csv".format(name)))
    result_df = pd.read_csv(os.path.join(basedir,"data/result_df_grouped_{0}.csv".format(name)))
    #result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedMonth'] = result_df['CreatedDate'].dt.month
    result_df['CreatedYear'] = result_df['CreatedDate'].dt.year
    
    result_df.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df_grouped = result_df.groupby(['CreatedYear','CreatedMonth'])['Invested_Value'].sum()
    
    result_df_grouped.to_csv(os.path.join(basedir,"data/result_df_grouped_1_{0}.csv".format(name)))
    result_df_grouped = pd.read_csv(os.path.join(basedir,"data/result_df_grouped_1_{0}.csv".format(name)))
    result_df_grouped.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df_grouped['Created'] = result_df_grouped['CreatedYear'].astype(str) + ' : ' + result_df_grouped['CreatedMonth'].astype(str)
    
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot()
    img = BytesIO()
    #ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.plot(result_df_grouped.Created, result_df_grouped.Invested_Value)
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
    vol_list = [(-0.10/252) * 30, 0,(0.10/252) * 30  ]
    basedir = os.path.abspath(os.path.dirname(__file__))
    portfolio = pd.DataFrame()
    portfolio_file = os.path.join(basedir, 'data/' + portfolioname + '.csv')
    portfolio = pd.read_csv(portfolio_file)

    climate_file = os.path.join(basedir, 'data/climate_master.csv')
    climate_data = pd.DataFrame()
    climate_data = pd.read_csv(climate_file)

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
            vol = random.choice(vol_list)
            if query_fossil.empty == False and query_fossil['Ticker'].iloc[0] == row['Ticker']:
                query_corr= corr_data.query('Country ==\'' + row['Country']+ '\'')
                query_corr = query_corr[query_corr['Measure'].str.contains("Fossil")]
                if query_corr.empty == True:
                    corr = 0
                else:
                    corr = query_corr['Stock_Price'].mean()
                    #if isinstance(corr, pd.Series):
                     #   corr = corr['Stock_Price'].mean()
                newStockPrice = prevStockPrice * (1 - calculate_SAD(row['Latitude'],str(previousMonthDate)) - (corr/12) - discount_rate + vol+ growth_rate)
            else:
                newStockPrice = prevStockPrice * (1 - discount_rate + vol + growth_rate)
            a_df_temp = a_df_temp.append({'Company':row['Company'],'Country':row['Country'],'Ticker':row['Ticker'],'Quantity':row['Quantity'], 'CreatedDate':nextMonthDate,'Stock_Price':newStockPrice,'Invested_Value':row['Quantity'] * newStockPrice}, ignore_index=True)
            print(prevStockPrice)
            previousMonthDate = nextMonthDate
    print(a_df_temp)
    a_df_temp = a_df_temp.append(portfolio)
    a_df_temp.to_csv(output_file)
    return 'Model ran successfully!!'

if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)
