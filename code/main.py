# main.py

from datetime import datetime
import helpers

# Datos de entrada
file_path = 'C:/Users/carsk/OneDrive - KU Leuven/Thesis/Revised_RESULTS/Charlotes comparition/9modeledStns.csv'
station_code = 'C01'
date1 = datetime.strptime('01-01-2016 00:00', '%d-%m-%Y %H:%M')
date2 = datetime.strptime('01-03-2016 00:00', '%d-%m-%Y %H:%M')
avg_date1 = datetime.strptime('01-01-2016 00:00', '%d-%m-%Y %H:%M')
avg_date2 = datetime.strptime('01-03-2016 00:00', '%d-%m-%Y %H:%M')

# Proceso
data = helpers.read_and_prepare_data(file_path)
filtered_data = helpers.filter_data_by_date(data, date1, date2)
average_df = helpers.calculate_average(data, avg_date1, avg_date2, station_code)
baseflow = helpers.create_baseflow_df(date1, date2, average_df)
station_without_baseflow = helpers.calculate_without_baseflow(filtered_data, baseflow, station_code)

print(station_without_baseflow[0:20])
