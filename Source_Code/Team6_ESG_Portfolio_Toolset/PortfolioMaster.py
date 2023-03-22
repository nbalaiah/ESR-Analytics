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
   data_file = os.path.join(basedir, 'data/' + name + '.csv')
   portfolio = pd.read_csv(data_file)
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
   
   return render_template('portfolio.html', tables=[data.to_html()], titles=[''])

   #return jsonify(WORDS)
    #return render_template('simple.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)
