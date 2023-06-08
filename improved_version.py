# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 23:10:20 2023

@author: carsk
"""

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio

# Function to do the processing
def process_period(data, start_date, end_date, avg_start_date, avg_end_date, station_code, model_station_code):
    # Filter the dataframe by dates
    filtered_data = data[(data['date'] >= start_date) & (data['date'] <= end_date)]
    
    average_data= data[(data['date'] >= avg_start_date) & (data['date'] <= avg_end_date)]
    
    # Extract only the time part of the dates
    average_data['time'] = average_data['date'].dt.time
    
    # Group by time and calculate the average of the station column
    average_df = average_data.groupby('time')[station_code].mean().reset_index()
    
    # Rename the station code column to 'Average'
    average_df.rename(columns={station_code: 'Average'}, inplace=True)
    
    # Create a DataFrame with a date range from date1 to date2
    baseflow = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date, freq='5T'))
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
    
    # Reindex the station data to match baseflow's index
    if 'date' in filtered_data.columns:
        filtered_data.set_index('date', inplace=True)
    
    # Create a new DataFrame with original station data
    station_without_baseflow = filtered_data[[station_code]].copy()
    
    # Subtract the baseflow from the station data and add it as a new column
    station_without_baseflow[f"{station_code}_without_baseflow"] = (((station_without_baseflow[station_code] - baseflow['Average']))/1000).clip(lower=0)
    
    # Insert the 'Average' column from baseflow in the middle of the 'station_without_baseflow' DataFrame
    station_without_baseflow.insert(1, 'Baseflow', baseflow['Average'])
    
    # Extract the modeled station data
    model_station_data = filtered_data[[model_station_code]].copy()
    model_station_data[model_station_code] = model_station_data[model_station_code] 
    
    # Merge the modeled station data with the 'station_without_baseflow' DataFrame
    station_without_baseflow = pd.merge(station_without_baseflow, model_station_data, how='left', left_index=True, right_index=True)

    return station_without_baseflow

# Read the CSV file
data = pd.read_csv('9modeledStns.csv')

# Convert the 'date' column to datetime
data['date'] = pd.to_datetime(data['date'], format='%d/%m/%Y %H:%M')

# Ask the user for the station code
station_code = input('Please enter the station code: ').upper()

# Ask the user for the second station code
model_station_code = input('Please enter the modeled station code: ').upper()

# Check if the station code is valid
if station_code not in data.columns or model_station_code not in data.columns:
    print('The provided station code is not valid.')
else:
    final_df = pd.DataFrame()

    while True:
        try:
            # Ask the user for the dates
            print("Here select the range in data which you like to extract baseflow")
            date_str1 = input('Please enter the start date (DD-MM-YYYY HH:MM): ')
            date_str2 = input('Please enter the end date (DD-MM-YYYY HH:MM): ')
    
            # Convert the dates to datetime
            date1 = datetime.strptime(date_str1, '%d-%m-%Y %H:%M')
            date2 = datetime.strptime(date_str2, '%d-%m-%Y %H:%M')
            
            # Ask the user for the dates to calculate the average 5-minute discharge
            avg_date_str1 = input('Initial date for average calculation (DD-MM-YYYY HH:MM): ')
            avg_date_str2 = input('Final date for average calculation (DD-MM-YYYY HH:MM): ')
            
            # Convert the dates to datetime
            avg_date1 = datetime.strptime(avg_date_str1, '%d-%m-%Y %H:%M')
            avg_date2 = datetime.strptime(avg_date_str2, '%d-%m-%Y %H:%M')
        except ValueError:
            print('The provided date format is not valid.')
        
        # Process the period
        period_df = process_period(data, date1, date2, avg_date1, avg_date2, station_code, model_station_code)
        
        # Append to final dataframe
        final_df = pd.concat([final_df, period_df])
        
        # Ask the user if they want to add another period
        cont = input('Do you want to add another period? (Y/N) ')
        
        if cont.lower() != 'y':
            break

    print(final_df)

    # Plotting the data using matplotlib
    plt.figure(figsize=(12, 6))
    plt.plot(final_df.index, final_df[f"{station_code}_without_baseflow"], label=f"{station_code}_without_baseflow")
    plt.plot(final_df.index, final_df[model_station_code], label=model_station_code)
    plt.legend()
    plt.title('Time series plot of station data')
    plt.xlabel('Date')
    plt.ylabel('Discharge')
    plt.show()

    # Plotting the data using plotly
    fig = px.line(final_df.reset_index(), x='date', y=[f"{station_code}_without_baseflow", model_station_code])
    fig.show()

    # Save the plot as an HTML file
    pio.write_html(fig, 'output.html')

    # Save the final DataFrame as a CSV file
    final_df.to_csv('output.csv')
