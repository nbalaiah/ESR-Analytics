from flask import Flask, redirect, url_for, render_template, jsonify
from flask_paginate import Pagination, get_page_args
import os
import pandas as pd

app = Flask(__name__)

@app.route('/')
def show():
   return 'Portfolio'


@app.route('/portfolio/<name>')
def show_portfolio(name):
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
   invested_value_bench = benchmark.query('CreatedDate ==\'' + str(minDate) + '\'')['Invested_Value'].iloc[0]
   current_value_bench = benchmark.query('CreatedDate ==\'' + str(maxDate) + '\'')['Invested_Value'].iloc[0]
   data_benchmark = data_benchmark.append({'Invested_Value':invested_value_bench,'Current_Value':current_value_bench},ignore_index=True)
   for ticker in tickers:
        invested_value = portfolio.query('CreatedDate ==\'' + str(minDate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        current_value = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['Invested_Value'].iloc[0]
        climate_value = portfolio.query('CreatedDate ==\'' + str(maxDate) + '\' and Ticker ==\'' + ticker + '\'')['Climate'].iloc[0]
        data = data.append({'Ticker':ticker,'Invested_Value': invested_value,'Current_Value':current_value,'Climate': climate_value},ignore_index=True)

   return render_template('portfolio.html', portfolio_data=data.to_dict(orient='records'),benchmark_data=data_benchmark.to_dict(orient='records'),title='ESG Portfolio')


   #return jsonify(WORDS)
    #return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)
