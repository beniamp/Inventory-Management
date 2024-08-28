import streamlit as st
import pandas as pd
import plotly.graph_objects as go



# Reading data from CSV files
df = pd.read_csv('BalanceV2.csv')
df_orders = pd.read_csv('Orders.csv')
df_orders = df_orders[['ProductNameColor', 'Quantity', 'ColorName', 'Date_Formatted', 'Category']]
df_stocks = pd.read_csv('Stocks.csv')

# Page setting
st.set_page_config(layout="wide")

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Inject custom CSS to style the select box
# Display various filtered and calculated data
st.markdown("""
    <style>
    .custom-box {
        padding: 20px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        font-size: 18px;
        color: #ffffff; /* White text color */
        margin-bottom: 10px; /* Space between the box and table */
    }
    .box-brown { background-color: #803400; }
    .box-red { background-color: #db2c12; }
    .box-yellow { background-color: #fae525; }
    .box-green { background-color: #1aba47; }
    .box-grey { background-color: #d6d6d6; }
    .box-brown2 { background-color: #cc7700; }
    .box-dark { background-color: #2f2959; }

    /* Make tables displayed by st.write() take the full width */
    table {
        width: 100% !important;
    }

    /* Optionally adjust padding and margins if necessary */
    th, td {
        padding: 10px; /* Adjust padding for table cells */
    }
    </style>
""", unsafe_allow_html=True)


# Replace null dates with a placeholder in both DataFrames
df['Date'] = df['Date'].fillna('0000-00-00')
df = df[df['Date'] != '0000-00-00']
df_orders['Date_Formatted'] = df_orders['Date_Formatted'].fillna('0000-00-00')

# Convert dates to integer format
df['Date_value'] = df['Date'].str.replace('-', '').astype(str)
df_orders['Date_value'] = df_orders['Date_Formatted'].str.replace('-', '').astype(str)

# Sidebar for date selection
sorted_dates = sorted(df['Date'].unique())

# Slider for date range selection
start_idx, end_idx = st.slider(
    "Select Date Range",
    min_value=0,
    max_value=len(sorted_dates) - 1,
    value=(0, len(sorted_dates) - 1),
    step=1,
)

# Get the selected start and end dates
start_date = sorted_dates[start_idx]
end_date = sorted_dates[end_idx]

st.write(f"Selected date range: {start_date} to {end_date}")

# Convert selected dates to integer format
start_date_int = start_date.replace('-', '')
end_date_int = end_date.replace('-', '')

# Filter the data by the selected date range
filtered_df = df[
    (df['Date_value'] >= start_date_int) & (df['Date_value'] <= end_date_int)
]

# For df_orders, keep rows with null dates as well
filtered_df2 = df_orders[
    (df_orders['Date_value'] >= start_date_int) & (df_orders['Date_value'] <= end_date_int) |
    (df_orders['Date_Formatted'] == '0000-00-00')
]

# Count the number of unique dates in the range
count_dates = len(filtered_df['Date'].unique())
st.write(f"Number of dates between selected range: {count_dates}")

# Warehouse filter with 'All options' option
warehouses = ['All options'] + df['Warehouse'].unique().tolist()
selected_warehouse = st.selectbox('Select Warehouse', warehouses)


if selected_warehouse == 'All options':
    # Group by 'Product' and sum 'MaxAvailability' across all warehouses
    product_data = filtered_df.groupby('Product').agg({'Volume': 'sum', 'Availability': 'sum'}).reset_index()
else:
    # Filter by the selected warehouse and group by 'Product'
    filtered_df = filtered_df[filtered_df['Warehouse'] == selected_warehouse]
    product_data = filtered_df.groupby('Product').agg({'Volume': 'sum', 'Availability': 'sum'}).reset_index()



# Category filter with 'All Categories' option
df['Category'] = df['Category'].replace('گوشی موبایل', 'گوشی موبایل ')
categories = ['All Categories'] + df['Category'].unique().tolist()
selected_category = st.selectbox('Select Category', categories)


# Filter DataFrame by selected category
if selected_category != 'All Categories':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    df_stocks = df_stocks[df_stocks['Category'] == selected_category]



# Brand filter with 'All Brands' option
if selected_category != 'All Categories':
    brands = filtered_df['Brand'].unique().tolist()
else:
    brands = df['Brand'].unique().tolist()

selected_brands = st.multiselect('Select Brand', brands, default=brands)

# Filter DataFrame by selected brands
if 'All Brands' not in selected_brands:
    filtered_df = filtered_df[filtered_df['Brand'].isin(selected_brands)]
    df_stocks = df_stocks[df_stocks['Brand'].isin(selected_brands)]  # Apply brand filter to stocks as well



# Display the final filtered data count
st.success(f"**Total products in selected filters:** {filtered_df.shape[0]}")



# Aggregating stock data by Name, Category, Brand, Warehouse
agg_stock = df_stocks.groupby(['ProductColorName', 'Category', 'Brand', 'Color', 'Warehouse'], as_index=False).agg({'Quantity': 'sum'}).rename(columns={
    'Quantity': 'Quantity_stock',
    'Category': 'CategoryS',
    'Brand': 'BrandS',
    'Color': 'ColorS'
})

# Merging aggregated stock data with filtered orders
merged_df = pd.merge(filtered_df2, agg_stock, left_on='ProductNameColor', right_on='ProductColorName', how='right')

# Filter the DataFrame where Date_Formatted is NaN and Quantity_stock is not 0
df8 = merged_df[(merged_df['Date_Formatted'].isna()) & (merged_df['Quantity_stock'] != 0)]

# Replace values based on the given conditions
df8['Quantity'] = df8['Quantity'].fillna(0)
df8 = df8[['ProductColorName', 'Quantity', 'Quantity_stock']].reset_index(drop=True)
df8 = df8.rename(columns={'Quantity': 'TotalVolume', 'Quantity_stock': 'MaxAvailability'})

# Calculate maximum availability for each product considering the warehouse
product_max_availability = filtered_df.groupby(['Product', 'Warehouse'])['Availability'].max().reset_index(name='MaxAvailability')

# Calculate the total volume ordered for each product
product_total_volume = filtered_df.groupby(['Product', 'Warehouse'])['Volume'].sum().reset_index(name='TotalVolume')

# Merge these two DataFrames on 'Product' and 'Warehouse'
product_data = pd.merge(product_total_volume, product_max_availability, on=['Product', 'Warehouse'])

# If "All options" is selected, aggregate across all warehouses
if selected_warehouse == 'All options':
    product_data = product_data.groupby('Product').agg({'TotalVolume': 'max', 'MaxAvailability': 'sum'}).reset_index()



# Define restock number
restock_number = 2

# Calculate Order Rate (Orders Per Day)
product_data['Order_Rate'] = product_data['TotalVolume'] / count_dates

# Calculate Stock Ratio
product_data['Restock_Ratio'] = product_data['Order_Rate'] / product_data['MaxAvailability'].replace(0, 0.1)

    
# Function to determine action status based on restock point
def determine_action_status(product_data):
    restock_point = product_data['Restock_Ratio']
    stock = product_data['MaxAvailability']

    if selected_category in ['کنسول بازی', 'تبلت', 'گوشی موبایل', ' گوشی موبایل', 'گوشی موبایل ']:
        if restock_point > 0.1 and round(product_data['MaxAvailability'] / product_data['Order_Rate']) == 0:
            return "Brown Type 1"
        elif 1 < round(product_data['MaxAvailability'] / product_data['Order_Rate']) < 2:
            return "Red"
        elif 2 < round(product_data['MaxAvailability'] / product_data['Order_Rate']) < 3:
            return "Yellow"
        elif 3 < round(product_data['MaxAvailability'] / product_data['Order_Rate']) < 7:
            return 'Green'
        elif 7 < round(product_data['MaxAvailability'] / product_data['Order_Rate']):
            return "Brown Type 2"
        else:
            return 'Grey'        


# Apply the function to determine action status
product_data['ActionStatus'] = product_data.apply(determine_action_status, axis=1)
product_data['DaysRemaining'] = round(product_data['MaxAvailability'] / product_data['Order_Rate'])


# drill down through each warehouse values
detailed_view = filtered_df.groupby(['Product', 'Warehouse'])['Availability'].max().reset_index()

# Create a search bar
search_query = st.text_input("Search for a Product", "")
if search_query:
    filtered_detailed_view = detailed_view[detailed_view['Product'].str.contains(search_query, case=False)]
    
    # Display a message if no products are found
    if filtered_detailed_view.empty:
        st.warning(f"No products found matching '{search_query}'.")
    else:
        # Display the detailed view for the searched product
        st.write(f"Details of warehouse for products matching: '{search_query}'")
        st.dataframe(filtered_detailed_view)


st.dataframe(product_data)
# Display various filtered and calculated data
st.markdown("""
    <style>
    .custom-box {
        padding: 20px;
        border-radius: 5px;
        font-weight: bold;
        text-align: center;
        font-size: 18px;
        color: #ffffff; /* White text color */
        margin-bottom: 10px; /* Space between the box and table */
    }
    .box-brown { background-color: #803400; }
    .box-red { background-color: #db2c12; }
    .box-yellow { background-color: #fae525; }
    .box-green { background-color: #1aba47; }
    .box-grey { background-color: #d6d6d6; }
    .box-brown2 { background-color: #cc7700; }
    </style>
    <div class="custom-box box-brown">
        💩
    </div>
""", unsafe_allow_html=True)



st.write("موجودی صفر / سفارش بالا ")
product_brown1 = product_data[product_data['ActionStatus'] == 'Brown Type 1'].reset_index(drop=True)
st.dataframe(product_brown1)
st.caption(f"Number of Products: {product_data[product_data['ActionStatus'] == 'Brown Type 1'].shape[0]}")

st.markdown("""
    <div class="custom-box box-red">
        🚨 
    </div>
""", unsafe_allow_html=True)
st.write("موجود کردن در اولین فرصت")
product_red = product_data[product_data['ActionStatus'] == 'Red'].reset_index(drop=True)
st.dataframe(product_red)
st.caption(f"Number of Products: {product_data[product_data['ActionStatus'] == 'Red'].shape[0]}")

st.markdown("""
    <div class="custom-box box-yellow">
        📅
    </div>
""", unsafe_allow_html=True)
st.write("برنامه ریزی برای موجود کردن کالا")
product_yellow = product_data[product_data['ActionStatus'] == 'Yellow'].reset_index(drop=True)
st.dataframe(product_yellow)
st.caption(f"Number of Products: {product_data[product_data['ActionStatus'] == 'Yellow'].shape[0]}")

st.markdown("""
    <div class="custom-box box-green">
        🙌
    </div>
""", unsafe_allow_html=True)
st.write("حاشیه نسبتا امن موجودی کنونی")
product_green = product_data[product_data['ActionStatus'] == 'Green'].reset_index(drop=True)
st.dataframe(product_data[product_data['ActionStatus'] == 'Green'])
st.caption(f"Number of Products: {product_data[product_data['ActionStatus'] == 'Green'].shape[0]}")

st.markdown("""
    <div class="custom-box box-grey">
        ❓
    </div>
""", unsafe_allow_html=True)
st.write("کالاهای مریض")
product_grey = product_data[product_data['ActionStatus'] == 'Grey'].reset_index(drop=True)
st.dataframe(product_grey)
st.caption(f"Number of Products: {product_data[product_data['ActionStatus'] == 'Grey'].shape[0]}")

st.markdown("""
    <div class="custom-box box-brown2">
        🙊🙈🙉
    </div>
""", unsafe_allow_html=True)
st.write("(فروش کم) موجودی بیش از میزان تقاضا")
prdocut_brown2 = product_data[product_data['ActionStatus'] == 'Brown Type 2'].reset_index(drop=True)
st.dataframe(prdocut_brown2)
st.caption(f"Number of Products: {product_data[product_data['ActionStatus'] == 'Brown Type 2'].shape[0]}")

st.markdown("""
    <div class="custom-box box-dark">
        ☠️ 
    </div>
""", unsafe_allow_html=True)
st.write("(فروش صفر) موجودی بیش از میزان تقاضا")
st.dataframe(df8)
st.caption(f"Number of Products: {df8.shape[0]}")


