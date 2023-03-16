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

def download_data():
    URL = 'https://fossilfreefunds.org/how-it-works'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    urls = []
    names = []
    dates = []
    linkMain='https://iyv-charts.s3-us-west-2.amazonaws.com/files/Invest+Your+Values+company+screens+{0}.xlsx'
    for i, link in enumerate(soup.findAll('a')):
        #print(link)
        FULLURL = link.get('href')
        if bool(re.search('company=', FULLURL)):
            urls.append(FULLURL)
            strVal = os.path.basename(soup.select('a')[i].attrs['href'])
            strVal = strVal.replace('download-data?company=','')
            date = datetime.strptime(strVal, '%Y%m%d').strftime('%m/%d/%Y')
            names.append(strVal)
            dates.append(date)
    print(names)
    
    names_urls = zip(names, urls)
    for name, url in names_urls:
        print("Download file: "+name)
        r = requests.get(linkMain.format(name), verify=False,stream=True)
        r.raw.decode_content = True
        with open("kaggle\\"+name+".xlsx", "wb") as out:
                shutil.copyfileobj(r.raw, out)   


def data_aggregation():
    companies = pd.DataFrame()
    files = os.listdir("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle") 
    for name in files:
        print(name)
        excel_data_df = pd.read_excel('C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\{0}'.format(name), sheet_name='Companies')
        excel_data_df["CreatedDate"] = datetime.strptime(name.replace(".xlsx",""), '%Y%m%d').strftime('%m/%d/%Y')
        print(excel_data_df)
        companies = companies.append(excel_data_df)
    companies.to_csv('companies_temp.csv')
    return(companies)

def data_preparation():
     companies = pd.read_csv('companies_temp.csv')
     companies = companies[companies['Country'].notna()]
     companies = companies[companies['Tickers'].notna()]
     companies.update(companies[['Fossil Free Funds: Fossil fuel finance risk score','Fossil Free Funds: Fossil fuel insurance risk score']].fillna(0))
     companies.update(companies.fillna('N'))
     return(companies)

def data_country_selection():
    companies = pd.DataFrame()
    companies = data_preparation()
    df = companies.query( "Country in ('Venezuela','Argentina','France','Mauritius','India', 'United States', 'China', 'Ukraine','Virgin Islands, British', 'Bangladesh','Cayman Islands')")
    df.to_csv('companies_final_draft.csv')

def data_split_countrywise():
     df = pd.read_csv('companies_final_draft.csv')
     lstCountries = df['Country'].unique()
     for country in lstCountries:
          df_country = df.query("Country in ('{0}')".format(country))
          df_country.to_csv('kaggle\\country\\{0}.csv'.format(country))

def data_update_stock_price(companies):
    companies_final = pd.DataFrame()
    for index, row in companies.iterrows():
    #print(row)
        try:
            
            r, data = Get_Yahoo_Data(row['CreatedDate'],row['Tickers'])
            #print(row['CreatedDate'])
            #print(data['Close'][0])
            row['Ticker'] = r
            row['Stock_Price'] = 0
            if (data.empty == False and data['Close'].empty == False):
                row['Stock_Price'] = data.iloc[0][1]      
            companies_final = companies_final.append(row)
            val = index
        except:
            print('error')
    return(companies_final)

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

def stock_price_updation():
    files = os.listdir("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country") 
    for name in files:
        print(name)
        if name != 'stock':
            companies = pd.read_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country\\" + name)
            companies_stock = data_update_stock_price(companies)
            companies_stock.to_csv("kaggle\\country\\{0}_stock.csv".format(name.replace(".csv","")))

#data_country_selection()
#data_split_countrywise()
stock_price_updation()