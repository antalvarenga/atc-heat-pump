import json 
import pandas as pd
import numpy as np



def get_temperature_array_JSON_Format(start_date, end_date):
    with open('../data/temp_data.json') as json_file:
        data = json.load(json_file)
    df = pd.DataFrame(data)
    df['dt'] = pd.to_datetime(df['dt'], unit='s')

    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    df_day = df[(df['dt'].dt.date >= start_date) & (df['dt'].dt.date <= end_date)]
    temperature_array = df_day['temp'].to_list()

    #split the array into arrays of 24 hours
    temperature_array = [temperature_array[i:i+24] for i in range(0, len(temperature_array), 24)]

    
    json_object = []

    for i in range(len(temperature_array)):
        #formar the date into a string Y%M%D
        date = start_date + pd.Timedelta(days=i)
        date = date.strftime('%Y-%m-%d')
        
        
        json_object.append({'date': date, 'hour': i, 'temperature': temperature_array[i]})


    return json_object

