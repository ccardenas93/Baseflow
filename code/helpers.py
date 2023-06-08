# helpers.py

import pandas as pd
from datetime import datetime

def read_and_prepare_data(file_path):
    # Leer el archivo CSV
    data = pd.read_csv(file_path)

    # Convertir la columna 'date' a datetime
    data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y %H:%M')

    return data

def filter_data_by_date(data, date1, date2):
    # Filtrar el dataframe por fechas
    filtered_data = data[(data['date'] >= date1) & (data['date'] <= date2)]
    return filtered_data

def calculate_average(data, avg_date1, avg_date2, station_code):
    average_data= data[(data['date'] >= avg_date1) & (data['date'] <= avg_date2)]
    average_data['time'] = average_data['date'].dt.time
    average_df = average_data.groupby('time')[station_code].mean().reset_index()
    average_df.rename(columns={station_code: 'Average'}, inplace=True)
    return average_df

def create_baseflow_df(date1, date2, average_df):
    baseflow = pd.DataFrame(index=pd.date_range(start=date1, end=date2, freq='5T'))
    baseflow.reset_index(inplace=True)
    baseflow.rename(columns={'index': 'date'}, inplace=True)
    baseflow['time'] = baseflow['date'].dt.time
    baseflow = pd.merge(baseflow, average_df, how='left', left_on='time', right_on='time')
    baseflow.drop(columns='time', inplace=True)
    baseflow.set_index('date', inplace=True)
    return baseflow

def calculate_without_baseflow(filtered_data, baseflow, station_code):
    if 'date' in filtered_data.columns:
        filtered_data.set_index('date', inplace=True)
    station_without_baseflow = filtered_data[[station_code]].copy()
    station_without_baseflow[f"{station_code}_without_baseflow"] = ((station_without_baseflow[station_code] - baseflow['Average'])/1000).clip(lower=0)
    station_without_baseflow.insert(1, 'Baseflow', baseflow['Average'])
    return station_without_baseflow
