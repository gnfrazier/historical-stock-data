#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import glob
import pandas as pd
import requests



files = glob.glob("*.csv")

# prevent reprocessing the output file
files.remove('stocks.csv')


def extract_stock_name(uri):
    
    html = requests.get(uri)

    soup = BeautifulSoup(html.text, 'html.parser')

    raw_title = soup.title.string

    stock_name = raw_title.split(' Historical')[0]
    
    return stock_name



file = files[3]
data = {}

for file in files:

    # Extract the stock symbol from the file name
    name = file.replace(".csv", "")
        
    # Load the data frame
    df = pd.read_csv(file)

    # Add the stock symbol as a value to the symbol column
    df['Symbol'] = name.upper()
    
    url = 'https://www.nasdaq.com/market-activity/stocks/' + name + '/historical'
    
    # Add data source reference
    df['Data Source'] = url
    
    # Add official stock name
    df['Stock Name'] = extract_stock_name(url)

    # Convert the date column to datetime data type
    df['Date'] = pd.to_datetime(df['Date'])

    # Convert the price column to a decimal number
    try:
        df[' Close/Last'] = df[' Close/Last'].str.strip(' $').astype(float)
        
    except AttributeError:
        # the indexes are not passed as a dollar value
        df[' Close/Last'] = df[' Close/Last'].astype(float)
        

    # Extract the closing price of the earliest date in the data frame
    first_value = df[' Close/Last'][(df['Date'] == df['Date'].min()) == True].squeeze()

    # Calculate the percent change column
    df['percent_change'] = df[' Close/Last']/first_value * 100

    # Convert to a integer
    df['percent_change'] = df['percent_change'].astype(int)

    # Add the dataframe to the dictionary, using the symbol for the key
    data[name] = df


# Combine the dataframes into a single dataset
all_symbols = pd.concat(data.values())

# Output the dataset to csv
all_symbols.to_csv('stocks.csv')

