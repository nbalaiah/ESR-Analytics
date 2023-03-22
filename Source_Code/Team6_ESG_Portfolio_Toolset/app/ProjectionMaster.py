from flask import Flask, redirect, url_for, render_template, jsonify
import os
import pandas as pd

app = Flask(__name__)

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
    return render_template('projection.html', projection_data=pd_result.to_dict(orient='records'),title='Climate Data Projection 2050')

if __name__ == '__main__':
    #app.debug = True
    app.run()
    #app.run(debug = True)