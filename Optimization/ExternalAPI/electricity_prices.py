from datetime import datetime, timedelta
import os
import numpy as np
from pandas import read_csv
from flask import Flask, jsonify, request

def read_prices(t0: datetime, t1: datetime):

    t = t0
    delta = timedelta(days=1)

    folder_name = '../data/marginalpdbcpt_2021/'

    file_index = dict()
    for fname in os.listdir(folder_name):
        key = fname.split('_')[1].split('.')[0]  # YearMonthDay string
        file_index[key] = fname

    price_series_list = []   
    while t <= t1:
        key = t.strftime("%Y%m%d")
        fname = file_index[key]
        data = read_csv(folder_name + fname, sep=';', skipfooter=1).to_numpy()
        price_series = data[:, -2] / 1000
        price_series_list.append(price_series)
        t += delta
        #print(t)
        #print(price_series.tolist())

    return price_series_list


def read_prices_JSON_Format(t0: datetime, t1: datetime):

    t = t0
    delta = timedelta(days=1)

    folder_name = '../data/marginalpdbcpt_2021/'

    file_index = dict()
    for fname in os.listdir(folder_name):
        key = fname.split('_')[1].split('.')[0]  # YearMonthDay string
        file_index[key] = fname

    price_series_list = []   
    while t <= t1:
        key = t.strftime("%Y%m%d")
        fname = file_index[key]
        data = read_csv(folder_name + fname, sep=';', skipfooter=1).to_numpy()
        price_series = data[:, -2] / 1000
        price_series_list.append(price_series)
        t += delta
        #print(t)
        #print(price_series.tolist())

    #print(price_series_list)
    #return price_series_list
    #creat json object to return
    json_object = []
    
    for i in range(len(price_series_list)):
        for hour in range(24):
            json_object.append({'date': t0 + timedelta(days=i), 'hour': hour, 'price': price_series_list[i][hour]})
        


    return json_object



if __name__ == "__main__":
    t0 = datetime.fromisoformat('2021-12-01')
    t1 = datetime.fromisoformat('2021-12-31')
    read_prices(t0, t1)