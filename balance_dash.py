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
df = pd.read_csv('BalanceV2.csv')




# Custom date range filter using selectbox
dates = df['Date'].unique()
dates = sorted(dates)  # Sort the dates in ascending order

# Sidebar for date selection using selectbox
st.header("Select Date Range")

selected_start_date = st.selectbox('Start Date', dates, index=0)
selected_end_date = st.selectbox('End Date', dates, index=len(dates)-1)


# Filter the DataFrame based on the selected dates
filtered_df = df[(df['Date'] >= selected_start_date) & (df['Date'] <= selected_end_date)]


# Sidebar for date selection
# sorted_dates = sorted(df['Date'].unique())


# Display the filtered data and count
st.write(f"Filtered Data from {selected_start_date} to {selected_end_date}:")
st.write(filtered_df)



