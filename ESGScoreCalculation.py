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
from sklearn.preprocessing import LabelEncoder

weights = [['Fossil',0.5],
               ['Deforestation',0.1],
               ['Weapons',0.05],
               ['Gun',0.05],
               ['Tobacco',0.1],
               ['Gender Equality',0.1],
               ['Prison',0.1],
               ['War',0.1],
               ['Political',0.1],
               ['Sealevel',0.1]]

def data_encoding(df):
    le = LabelEncoder()  
    #df['Country']=le.fit_transform(df['Country'])
    df['Fossil Free Funds: Coal screen']=le.fit_transform(df['Fossil Free Funds: Coal screen'])
    df['Fossil Free Funds: Oil / gas screen']=le.fit_transform(df['Fossil Free Funds: Oil / gas screen'])
    df['Fossil Free Funds: Macroclimate30 coal-fired utility screen']=le.fit_transform(df['Fossil Free Funds: Macroclimate30 coal-fired utility screen'])
    df['Fossil Free Funds: Fossil-fired utility screen']=le.fit_transform(df['Fossil Free Funds: Fossil-fired utility screen'])
    df['Fossil Free Funds: Clean200 screen']=le.fit_transform(df['Fossil Free Funds: Clean200 screen'])
    df['Deforestation Free Funds: Producer screen']=le.fit_transform(df['Deforestation Free Funds: Producer screen'])
    df['Deforestation Free Funds: Financier screen']=le.fit_transform(df['Deforestation Free Funds: Financier screen'])
    df['Deforestation Free Funds: Consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Consumer brand screen'])
    df['Deforestation Free Funds: Palm oil producer screen']=le.fit_transform(df['Deforestation Free Funds: Palm oil producer screen'])
    df['Deforestation Free Funds: Palm oil consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Palm oil consumer brand screen'])
    df['Deforestation Free Funds: Paper / pulp producer screen']=le.fit_transform(df['Deforestation Free Funds: Paper / pulp producer screen'])
    df['Deforestation Free Funds: Paper / pulp consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Paper / pulp consumer brand screen'])
    df['Deforestation Free Funds: Rubber producer screen']=le.fit_transform(df['Deforestation Free Funds: Rubber producer screen'])
    df['Deforestation Free Funds: Rubber consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Rubber consumer brand screen'])
    df['Deforestation Free Funds: Timber producer screen']=le.fit_transform(df['Deforestation Free Funds: Timber producer screen'])
    df['Deforestation Free Funds: Timber consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Timber consumer brand screen'])
    df['Deforestation Free Funds: Cattle producer screen']=le.fit_transform(df['Deforestation Free Funds: Cattle producer screen'])
    df['Deforestation Free Funds: Cattle consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Cattle consumer brand screen'])
    df['Deforestation Free Funds: Soy producer screen']=le.fit_transform(df['Deforestation Free Funds: Soy producer screen'])
    df['Deforestation Free Funds: Soy consumer brand screen']=le.fit_transform(df['Deforestation Free Funds: Soy consumer brand screen'])
    df['Weapons Free Funds: Major military contractor screen']=le.fit_transform(df['Weapons Free Funds: Major military contractor screen'])
    df['Weapons Free Funds: Cluster munitions / landmines screen']=le.fit_transform(df['Weapons Free Funds: Cluster munitions / landmines screen'])
    df['Weapons Free Funds: Nuclear weapons screen']=le.fit_transform(df['Weapons Free Funds: Nuclear weapons screen'])
    df['Gun Free Funds: Gun manufacturers screen']=le.fit_transform(df['Gun Free Funds: Gun manufacturers screen'])
    df['Gun Free Funds: Gun retailers screen']=le.fit_transform(df['Gun Free Funds: Gun retailers screen'])
    df['Tobacco Free Funds: Tobacco producers screen']=le.fit_transform(df['Tobacco Free Funds: Tobacco producers screen'])
    df['Tobacco Free Funds: Tobacco-promoting entertainment companies screen']=le.fit_transform(df['Tobacco Free Funds: Tobacco-promoting entertainment companies screen'])
    df['Gender Equality Funds: Has Equileap gender equality score']=le.fit_transform(df['Gender Equality Funds: Has Equileap gender equality score'])
    df['Prison Free Funds: Prison industry screen']=le.fit_transform(df['Prison Free Funds: Prison industry screen'])
    df['Prison Free Funds: Border industry screen']=le.fit_transform(df['Prison Free Funds: Border industry screen'])
    df['Prison Free Funds: Higher risk screen']=le.fit_transform(df['Prison Free Funds: Higher risk screen'])
    df['Prison Free Funds: Private prison operators screen']=le.fit_transform(df['Prison Free Funds: Private prison operators screen'])
    df['Fossil Free Funds: Fossil fuel finance screen']=le.fit_transform(df['Fossil Free Funds: Fossil fuel finance screen'])
    df['Fossil Free Funds: Fossil fuel finance risk score']=le.fit_transform(df['Fossil Free Funds: Fossil fuel finance risk score'])
    df['Fossil Free Funds: Fossil fuel insurance screen']=le.fit_transform(df['Fossil Free Funds: Fossil fuel insurance screen'])
    df['Fossil Free Funds: Fossil fuel insurance risk score']=le.fit_transform(df['Fossil Free Funds: Fossil fuel insurance risk score'])

    return(df)

def calculate_Corr():
    files = os.listdir("kaggle\\country\\stock") 
    for name in files:
        print(name)
        if (name != 'Corr' and name !='ESGScore'):
            companies = pd.read_csv("kaggle\\country\\stock\\" + name)
            df = companies.loc[:, ~companies.columns.str.contains('^Unnamed')]
            df = data_encoding(df)
            outputD = pd.DataFrame()
            outputD =df.corr(method ='kendall')['Stock_Price']
            #outputD.rename(columns = {"" : "Measure"}, inplace = True)
            outputD.to_csv("kaggle\\country\\stock\\Corr\\{0}_Corr.csv".format(name.replace('csv','')))

#calculate_Corr()

def isColContainsInWeights(name, weights):
    for weight in weights:
        if weight[0] in name:
            return True
    return False

def ESGScore_Calculation():
    companies = pd.read_csv("companies_master.csv")
    df = companies.loc[:, ~companies.columns.str.contains('^Unnamed')]
    df = companies.loc[:, ~companies.columns.str.contains('^Tickers')]
    #df = data_encoding(df)   
    final_result = pd.DataFrame()                            
    for index, row in df.iterrows(): 
        ESGScore = 0 
        valColumn = 0 
        allColumn = 0      
        for weight in weights:
            #cols = [col for col in df.columns if weight[0] in col]         
            for col in df.columns:
                #print(col)
                if isColContainsInWeights(col, weights):
                    print(col + '  : ' + str(row[col]))
                    allColumn = allColumn + 1
                    if(row[col] == 'Y'):
                        valColumn = valColumn + weight[1]
        ESGScore = (valColumn / allColumn) * 100
        row['ESGScore'] = ESGScore
        final_result = final_result.append(row)
    final_result.to_csv("companies_master_ESG.csv")

                    
ESGScore_Calculation()

def generate_master_file():
    files = os.listdir("kaggle\\country\\stock") 
    final_result = pd.DataFrame()
    for name in files:
        #print(name)
        
        if (name != 'Corr' and name != 'ESGScore'):
            companies = pd.read_csv("kaggle\\country\\stock\\" + name)
            df = companies.loc[:, ~companies.columns.str.contains('^Unnamed')]
            df = companies.loc[:, ~companies.columns.str.contains('^Tickers')]
            final_result = final_result.append(df)

    final_result = final_result.query('Stock_Price > 0')    
    final_result.to_csv("kaggle\\country\\stock\\companies_master.csv")

#generate_master_file()

def Is_True(row, cols):
    for col in cols:
        if row[col] == 'Y':
            return True
    return False

def split_data_climate_categories(weights):
    companies = pd.read_csv("companies_master.csv")
    companies = companies.query("CreatedDate == \'3/9/2023\'")
    for weight in weights:
        cols = [col for col in companies.columns if weight[0] in col]
        df_result = pd.DataFrame()
        for index, row in companies.iterrows():
            if Is_True(row,cols):
                new = [[row['Company'],row['Country'],row['Ticker']]]
                df_result = df_result.append(new)
        df_result.to_csv("data\\{0}.csv".format(weight[0]))
    companies_war = companies.query("Country == \'Ukraine\'")
    companies_war = companies_war[['Company','Country','Ticker']]
    companies_war.to_csv("data\\{0}.csv".format("war"))

    companies_political = companies.query("Country == \'Venezuela\'")
    companies_political = companies_political[['Company','Country','Ticker']]
    companies_political.to_csv("data\\{0}.csv".format("political"))

    companies_sealevel = companies.query("Country in (\'Cayman Islands\',\'Virgin Islands, British\',\'Mauritius\')")
    companies_sealevel = companies_sealevel[['Company','Country','Ticker']]
    companies_sealevel.to_csv("data\\{0}.csv".format("sealevel"))

#split_data_climate_categories(weights)

#ESGScore_Calculation()

def write_weights_file():
    weights_pd = pd.DataFrame(weights)
    weights_pd.to_csv("data\\{0}.csv".format("weights"))

#write_weights_file()
