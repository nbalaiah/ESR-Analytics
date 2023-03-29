from flask import Flask, redirect, url_for, render_template, make_response, jsonify
from flask_restx import Api, Resource, fields
import pandas as pd
import os
app = Flask(__name__)
api = Api(app, version='1.0', title='GROW - ESG Analytics API')
ns = api.namespace('api')

basedir = os.path.abspath(os.path.dirname(__file__))

@ns.route('/stocks')
class Stocks(Resource):
   def get(self):
      csv_sample_master = os.path.join(basedir, 'data/portfolio_sample_master.csv')
      df_sample_master = pd.read_csv(csv_sample_master)
      stocks = df_sample_master['Ticker'].unique().tolist()
      stocks.sort()
      return jsonify(stocks)
   
@ns.route('/portfolios')
class Portfolios(Resource):
   def get(self):
      csv_portfolio_list = os.path.join(basedir, 'data/portfolio_list.csv')
      df_portfolio_list = pd.read_csv(csv_portfolio_list)
      portfolios = df_portfolio_list['Name'].unique().tolist()
      portfolios.sort()
      return jsonify(portfolios)


if __name__ == '__main__':
    app.run(debug = True, port = 5001)