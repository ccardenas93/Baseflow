# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 20:06:57 2023

@author: carsk
"""


import pandas as pd
from datetime import datetime
##########################################EXTRACTING BASEFLOW##############################################
# Read the CSV file
data = pd.read_csv('9modeledStns.csv')

# Convert the 'date' column to datetime
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y %H:%M')

# Ask the user for the station code
station_code = input('Please enter the station code: ').upper()

# Check if the station code is valid
if station_code not in data.columns:
    print('The provided station code is not valid.')
else:
    # Ask the user for the dates
    try:
        print("Here select the range in data which you like to extract basefloww")
        date_str1 = input('Please enter the start date (DD-MM-YYYY HH:MM): ')
        date_str2 = input('Please enter the end date (DD-MM-YYYY HH:MM): ')

        # Convert the dates to datetime
        date1 = datetime.strptime(date_str1, '%d-%m-%Y %H:%M')
        date2 = datetime.strptime(date_str2, '%d-%m-%Y %H:%M')
    except ValueError:
        print('The provided date format is not valid.')

    # Filter the dataframe by dates
    filtered_data = data[(data['date'] >= date1) & (data['date'] <= date2)]

    # Ask the user for the dates to calculate the average 5-minute discharge
    try:
        avg_date_str1 = input('Initial date for average calculation (DD-MM-YYYY HH:MM): ')
        avg_date_str2 = input('Final date for average calculation (DD-MM-YYYY HH:MM): ')

        # Convert the dates to datetime
        avg_date1 = datetime.strptime(avg_date_str1, '%d-%m-%Y %H:%M')
        avg_date2 = datetime.strptime(avg_date_str2, '%d-%m-%Y %H:%M')
    except ValueError:
        print('The provided date format is not valid.')

    average_data= data[(data['date'] >= avg_date1) & (data['date'] <= avg_date2)]

    # Extract only the time part of the dates
    average_data['time'] = average_data['date'].dt.time

    # Group by time and calculate the average of the station column
    average_df = average_data.groupby('time')[station_code].mean().reset_index()

    # Rename the station code column to 'Average'
    average_df.rename(columns={station_code: 'Average'}, inplace=True)

    print(average_df)

    # Create a DataFrame with a date range from date1 to date2
    baseflow = pd.DataFrame(index=pd.date_range(start=date1, end=date2, freq='5T'))
    baseflow.reset_index(inplace=True)
    baseflow.rename(columns={'index': 'date'}, inplace=True)

    # Extract only the time part of the dates
    baseflow['time'] = baseflow['date'].dt.time

    # Merge baseflow with average_df, making the values repeat until the date range is complete
    baseflow = pd.merge(baseflow, average_df, how='left', left_on='time', right_on='time')

    # Remove the 'time' column
    baseflow.drop(columns='time', inplace=True)

    # Make sure the dates are in the index for easy data manipulation in the future
    baseflow.set_index('date', inplace=True)

    print(baseflow)

    # Reindex the station data to match baseflow's index
    if 'date' in filtered_data.columns:
        filtered_data.set_index('date', inplace=True)
    
    # Create a new DataFrame with original station data
    station_without_baseflow = filtered_data[[station_code]].copy()
    
    # Subtract the baseflow from the station data and add it as a new column
    station_without_baseflow[f"{station_code}_without_baseflow"] = (((station_without_baseflow[station_code] - baseflow['Average']))/1000).clip(lower=0)
    
    # Insert the 'Average' column from baseflow in the middle of the 'station_without_baseflow' DataFrame
    station_without_baseflow.insert(1, 'Baseflow', baseflow['Average'])
    
    print(station_without_baseflow)



    # Ask the user for the second station code
    model_station_code = input('Please enter the modeled station code: ').upper()
    
    # Check if the modeled station code is valid
    if model_station_code not in filtered_data.columns:
        print('The provided modeled station code is not valid.')
    else:
        # Extract the modeled station data
        model_station_data = filtered_data[[model_station_code]].copy()
        
        model_station_data[model_station_code] = model_station_data[model_station_code] 
    
        # Merge the modeled station data with the 'station_without_baseflow' DataFrame
        station_without_baseflow = pd.merge(station_without_baseflow, model_station_data, how='left', left_index=True, right_index=True)
    
        print(station_without_baseflow)

    
# Plotting the data
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(station_without_baseflow.index, station_without_baseflow[f"{station_code}_without_baseflow"], label=f"{station_code}_without_baseflow")
plt.plot(station_without_baseflow.index, station_without_baseflow[model_station_code], label=model_station_code)
plt.legend()
plt.title('Time series plot of station data')
plt.xlabel('Date')
plt.ylabel('Discharge')
plt.show()

 