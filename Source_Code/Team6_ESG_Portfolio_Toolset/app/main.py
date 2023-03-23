from flask import Flask, redirect, url_for, render_template, jsonify
import os
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

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

@app.route('/projection/<name>')
def show_projection(name):
    pd_result = pd.DataFrame()
    basedir = os.path.abspath(os.path.dirname(__file__))
    projection_file = os.path.join(basedir, 'data/projected_result.csv')
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
      
    result_df.to_csv(os.path.join(basedir,"result_df_grouped.csv"))
    result_df = pd.read_csv(os.path.join(basedir,"result_df_grouped.csv"))
    #result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedDate']= pd.to_datetime(result_df['CreatedDate'])
    result_df['CreatedMonth'] = result_df['CreatedDate'].dt.month
    result_df['CreatedYear'] = result_df['CreatedDate'].dt.year
    
    result_df.sort_values(['CreatedYear','CreatedMonth'],inplace=True)
    result_df_grouped = result_df.groupby(['CreatedYear','CreatedMonth'])['Invested_Value'].sum()
    
    result_df_grouped.to_csv(os.path.join(basedir,"result_df_grouped_1.csv"))
    result_df_grouped = pd.read_csv(os.path.join(basedir,"result_df_grouped_1.csv"))
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

    return render_template('projection.html', projection_data=pd_result.to_dict(orient='records'),plot_url=plot_url,title='Climate Data Projection 2050')


if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)
