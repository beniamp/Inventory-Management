import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from xlsxwriter import Workbook
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
#  Creating integer from date values
df['Date_value'] = df['Date'].str.replace('-', '').astype(str)


# Sidebar for date selection
sorted_dates = sorted(df['Date'].unique())

# Sidebar for date selection using selectbox
st.header("Select Date Range")
start_date = st.selectbox("Start Date", sorted_dates)
end_date = st.selectbox("End Date", sorted_dates, index=len(sorted_dates) - 1)

# Filter the data by the selected date range
filtered_df = df[(df['Date_value'] >= start_date) & (df['Date_value'] <= end_date)]

# Count the number of dates in the range
count_dates = len(filtered_df)

# Display the filtered data and count
st.write(f"Filtered Data from {start_date} to {end_date}:")
st.write(filtered_df)

st.write(f"Number of dates between selected range: {count_dates}")
