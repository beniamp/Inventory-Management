import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from xlsxwriter import Workbook
import numpy as np
#import pyodbc as odbc


# Defining the Component of Connection String
# DRIVER_NAME = "{ODBC Driver 17 for SQL Server}"
# SERVER_NAME = "aminpour-lap"
# DATABASE_NAME = "order_management"
# USERNAME = "DGSERVICE\b.aminpour"



#connection_string = f"""
#    DRIVER={DRIVER_NAME};
#    SERVER={SERVER_NAME};
#    DATABASE={DATABASE_NAME};
#    Trusted_Connection=yes;




#conn = odbc.connect(connection_string, pooling=False)
#cursor = conn.cursor()


# Returning All the Values from Fields and Records in Desired Table 
#query1 = """
#    SELECT * 
#    FROM order_management.dbo.orders_0101_0505
#"""

#result = cursor.execute(query1).fetchall()



# Coverting our Sql Based Table into Pandas Dataframe
#df_orders = pd.read_sql(query1, conn)
# Reading data from csv file
df = pd.read_csv('BalanceV2.csv')


# Replace null dates with a placeholder
df['Date'] = df['Date'].fillna('0000-00-00')
df = df[df['Date'] != '0000-00-00']

#  Creating integer from date values
df['Date_value'] = df['Date'].str.replace('-', '').astype(str)

# Sidebar for date selection
sorted_dates = sorted(df['Date'].unique())

# Sidebar for date selection using selectbox
st.header("Select Date Range")
start_date = st.selectbox("Start Date", sorted_dates)
end_date = st.selectbox("End Date", sorted_dates, index=len(sorted_dates) - 1)

# Filter the data by the selected date range
filtered_df = df[(df['Date_value'] >= start_date.replace('-', '')) & (df['Date_value'] <= end_date.replace('-', ''))]

# Count the number of unique dates in the range
count_dates = len(filtered_df['Date'].unique())

# Assuming 'ProductColorNameS' is the column name for product identifiers
# Calculate the total volume ordered for each product
product_total_volume = filtered_df.groupby('ProductColorNameS').size().reset_index(name='TotalVolume')

# Calculate maximum availability for each product
# Here we assume 'Availability' column contains max availability values for each product
product_max_availability = df.groupby('ProductColorNameS')['Availability'].max().reset_index(name='MaxAvailability')

# Merge these two DataFrames on 'ProductColorNameS' (Whole)
product_data = pd.merge(product_total_volume, product_max_availability, on='ProductColorNameS')
# Merge these two DataFrames on 'ProductColorNameS' (Brown)
product_data2 = pd.merge(product_total_volume, product_max_availability, on='ProductColorNameS')

# Define restock number
restock_number = 2


# Calculate Order Rate (Orders Per Day)
product_data['Order_Rate'] = product_data['TotalVolume'] / count_dates

# Calculate Stock Ratio
product_data['Restock_Ratio'] = product_data['Order_Rate'] / product_data['MaxAvailability'].replace(0, 0.1)



# Function to determine action status based on restock point
def determine_action_status(restock_point):
    if restock_point > 1:
        return "Brown Type 1"
    elif 0.1 < restock_point < 1 :
        return "Orange"
    elif  0.05 < restock_point < 0.1:
        return "Green"
    else:
        return "Brown Type 2"

# Apply the function to determine action status
product_data['ActionStatus'] = product_data['Restock_Ratio'].apply(determine_action_status)
product_data2 = product_data[product_data['ActionStatus'] == 'Brown Type 1']
product_data3 = product_data[product_data['ActionStatus'] == 'Orange']
product_data4 = product_data[product_data['ActionStatus'] == 'Green']
product_data5 = product_data[product_data['ActionStatus'] == 'Brown Type 2']


# Display the filtered data with the custom table outline
st.write(f"Filtered Data from {start_date} to {end_date}:")

st.write(product_data)
st.write(product_data2)
st.write(product_data3)
st.write(product_data4)
st.write(product_data5)



st.write(f"Number of dates between selected range: {count_dates}")
