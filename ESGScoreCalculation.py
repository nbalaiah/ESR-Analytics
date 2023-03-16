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
    files = os.listdir("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country\\stock") 
    for name in files:
        print(name)
        if (name != 'Corr'):
            companies = pd.read_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country\\stock\\" + name)
            df = companies.loc[:, ~companies.columns.str.contains('^Unnamed')]
            df = data_encoding(df)
            outputD = pd.DataFrame()
            outputD =df.corr(method ='kendall')['Stock_Price']
            outputD.to_csv("C:\\Users\\Dharshini\\Desktop\\Markets Workshop 2023\\kaggle\\country\\stock\\Corr\\{0}_Corr.csv".format(name.replace('csv','')))

calculate_Corr()


