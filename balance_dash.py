import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import pyodbc as odbc


# Defining the Component of Connection String
DRIVER_NAME = "{ODBC Driver 17 for SQL Server}"
SERVER_NAME = "aminpour-lap"
DATABASE_NAME = "order_management"
USERNAME = "DGSERVICE\b.aminpour"


connection_string = f"""
    DRIVER={DRIVER_NAME};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""



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
df = pd.read_csv('Balance.csv')
df.head()



# Create a figure with secondary y-axis
def category_bars(df):
    fig = make_subplots(specs=[[{'secondary_y': True}]])

    fig.add_trace(go.Bar(
    x=df['Category'], 
    y=df['Total_availability'], 
    name='Total Availability', 
    marker_color='orange'),
    secondary_y=True)




    fig.add_trace(go.Bar(
    x=df['Category'],
    y=df['Total_Volume'],
    name='Total Volume',
    marker_color='indianred'),
    secondary_y=True)


    fig.update_layout(
    title='Total Availability and Total Volume by Category',
    xaxis_title='Category',
    yaxis_title='Value',
    barmode='group',  # Group bars next to each other
    )

    fig.update_yaxes(title_text='Total Availability', secondary_y=True)
    fig.update_yaxes(title_text='Total Volume', secondary_y=True)

    return fig


# Unit Distribution charts by stock and volume
def unit_stock_distribution(df):
    df_filtered = df[df['Total_availability'] > 0]
    min_price= df['Base_Price'].min()
    max_price= 200000000
    bin_edges= [min_price + i*(max_price - min_price) / 80 for i in range(81)]
    bin_labels= [f'{int(bin_edges[i]):,} - {int(bin_edges[i+1]):,}' for i in range(len(bin_edges)-1)]
    df_filtered['PriceRange'] = pd.cut(df_filtered['Base_Price'], bins=bin_edges, labels=bin_labels, include_lowest=True)
    price_range_distribution = df_filtered.groupby('PriceRange').sum()[['Total_Volume']].reset_index()
    fig = px.bar(
        price_range_distribution, 
        x='PriceRange', 
        y='Total_Volume', 
        title='Distribution of Base Prices availability',
        color_discrete_sequence=['goldenrod'])

    return fig



# Scoreboards metrics
off_stock = df[df['Total_availability'] == 0].reset_index()
atp_products = df[df['Total_availability'] > df['Total_Volume']].reset_index()
over_stock = df[df['Total_availability'] < df['Total_Volume']].reset_index()



# Table off the stocks
def offstock_table(df):
    df_filtered = df[df['Total_availability'] == 0]
    df_filtered = df_filtered[['Product', 'Category', 'Brand', 'Color', 'Base_Price', 'Total_availability', 'Total_Volume']].sort_values(by='Total_Volume', ascending=False)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_filtered.columns),
            fill_color='dodgerblue',
            align='left'), 
        cells=dict(
            values=[df_filtered[col] for col in df_filtered.columns],
            fill_color='floralwhite',
            align='left'
        )
    )])

    fig.update_layout(title='Off The Stock Products')

    return fig



# Table over stocks
def overstock_table(df):
    df_filtered = df[(df['Total_availability'] > df['Total_Volume']) & (df['Total_Volume'] == 0)]
    df_filtered = df_filtered[['Product', 'Category', 'Brand', 'Color', 'Base_Price', 'Total_availability', 'Total_Volume']].sort_values(by='Total_availability', ascending=False)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_filtered.columns),
            fill_color='powderblue',
            align='left'), 
        cells=dict(
            values=[df_filtered[col] for col in df_filtered.columns],
            fill_color='floralwhite',
            align='left'
        )
    )])

    fig.update_layout(title='Over Stock Products')

    return fig



# Table ATP Products
def atp_table(df):
    df_filtered = df[df['Total_availability'] < df['Total_Volume']]
    df_filtered = df_filtered[['Product', 'Category', 'Brand', 'Color', 'Base_Price', 'Total_availability', 'Total_Volume']].sort_values(by='Total_Volume', ascending=False)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df_filtered.columns),
            fill_color='salmon',
            align='left'), 
        cells=dict(
            values=[df_filtered[col] for col in df_filtered.columns],
            fill_color='floralwhite',
            align='left'
        )
    )])

    fig.update_layout(title='High ATP Products')

    return fig




# Streamlit launch
# Streamlit app
st.title('Inventory Metrics Dashboard')

# Category filter
categories = df['Category'].unique()
selected_category = st.selectbox('Select Category', categories)

# Filter DataFrame by selected category
filtered_df = df[df['Category'] == selected_category]

# Compute metrics for the filtered DataFrame
off_stock = filtered_df[filtered_df['Total_availability'] == 0]
atp_products = filtered_df[filtered_df['Total_availability'] > filtered_df['Total_Volume']]
over_stock = filtered_df[filtered_df['Total_availability'] < filtered_df['Total_Volume']]

# Compute percentages
total_products = len(filtered_df)
off_stock_percentage = (len(off_stock) / total_products) * 100 if total_products > 0 else 0
atp_percentage = (len(atp_products) / total_products) * 100 if total_products > 0 else 0
over_stock_percentage = (len(over_stock) / total_products) * 100 if total_products > 0 else 0

# Display metrics
st.subheader(f'Total Off Stock in {selected_category}')
st.write(f"Count: {len(off_stock)}")
st.write(f"Percentage: {off_stock_percentage:.2f}%")

st.subheader(f'Total ATP (Available to Promise) in {selected_category}')
st.write(f"Count: {len(atp_products)}")
st.write(f"Percentage: {atp_percentage:.2f}%")

st.subheader(f'Total Over Stock in {selected_category}')
st.write(f"Count: {len(over_stock)}")
st.write(f"Percentage: {over_stock_percentage:.2f}%")