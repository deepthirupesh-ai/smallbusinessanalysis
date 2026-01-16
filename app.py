import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Page Config
st.set_page_config(page_title="Coffee Shop Business Analysis", layout="wide")

# Title and Intro
st.title("☕ Small Coffee Shop Business Analysis")
st.markdown("""
This dashboard provides an interactive overview of the coffee shop's performance.
The data is generated synthetically to simulate a real-world scenario.
""")

# Check for Database
if not os.path.exists('coffee_shop.db'):
    st.error("Database not found! Please run `python generate_data.py` first to generate the data.")
    st.stop()

# Database Connection
@st.cache_data
def load_data():
    conn = sqlite3.connect('coffee_shop.db')
    
    # Load DataFrames
    df_trans = pd.read_sql_query("SELECT * FROM transactions", conn)
    df_items = pd.read_sql_query("SELECT * FROM transaction_items", conn)
    df_products = pd.read_sql_query("SELECT * FROM products", conn)
    df_customers = pd.read_sql_query("SELECT * FROM customers", conn)
    
    conn.close()
    
    # Preprocessing
    df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date'])
    df_trans['hour'] = df_trans['transaction_date'].dt.hour
    df_trans['day_name'] = df_trans['transaction_date'].dt.day_name()
    df_trans['date'] = df_trans['transaction_date'].dt.date
    
    # Merge for detailed item analysis
    df_full_items = df_items.merge(df_products, left_on='product_id', right_on='id', suffixes=('_item', '_prod'))
    df_full_items = df_full_items.merge(df_trans[['id', 'transaction_date', 'hour', 'day_name']], left_on='transaction_id', right_on='id')
    
    return df_trans, df_items, df_products, df_customers, df_full_items

df_trans, df_items, df_products, df_customers, df_full_items = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df_trans['date'].min(), df_trans['date'].max()]
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df_trans['date'] >= start_date) & (df_trans['date'] <= end_date)
    df_trans_filtered = df_trans.loc[mask]
    
    # Filter full items based on transaction IDs in the filtered range
    valid_trans_ids = df_trans_filtered['id'].unique()
    df_full_items_filtered = df_full_items[df_full_items['transaction_id'].isin(valid_trans_ids)]
else:
    df_trans_filtered = df_trans
    df_full_items_filtered = df_full_items

# --- Key Metrics ---
st.subheader("Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)

total_revenue = df_trans_filtered['total_amount'].sum()
total_transactions = len(df_trans_filtered)
avg_transaction_value = df_trans_filtered['total_amount'].mean()
total_items_sold = df_full_items_filtered['quantity'].sum()

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Transactions", f"{total_transactions}")
col3.metric("Avg Order Value", f"${avg_transaction_value:,.2f}")
col4.metric("Items Sold", f"{total_items_sold}")

# --- Visualizations ---
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Sales Trends", "Product Performance", "Customer Insights"])

with tab1:
    st.subheader("Sales Trends")
    
    col_a, col_b = st.columns(2)
    
    # Daily Sales Trend
    with col_a:
        st.markdown("**Daily Revenue Trend**")
        daily_sales = df_trans_filtered.groupby('date')['total_amount'].sum().reset_index()
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=daily_sales, x='date', y='total_amount', marker='o', ax=ax1)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Revenue ($)")
        plt.xticks(rotation=45)
        st.pyplot(fig1)

    # Hourly Traffic
    with col_b:
        st.markdown("**Hourly Traffic (Heatmap)**")
        hourly_sales = df_trans_filtered.groupby('hour')['id'].count().reset_index(name='transaction_count')
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(data=hourly_sales, x='hour', y='transaction_count', palette="viridis", ax=ax2, hue='hour', legend=False)
        ax2.set_xlabel("Hour of Day")
        ax2.set_ylabel("Transactions")
        st.pyplot(fig2)

with tab2:
    st.subheader("Product Performance")
    
    col_c, col_d = st.columns(2)
    
    # Top Products
    with col_c:
        st.markdown("**Top 10 Selling Products**")
        top_products = df_full_items_filtered.groupby('name')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.barplot(data=top_products, y='name', x='quantity', palette="magma", ax=ax3, hue='name', legend=False)
        ax3.set_xlabel("Quantity Sold")
        ax3.set_ylabel("")
        st.pyplot(fig3)

    # Category Sales
    with col_d:
        st.markdown("**Revenue by Category**")
        category_sales = df_full_items_filtered.groupby('category')['price_at_transaction'].sum().reset_index()
        fig4, ax4 = plt.subplots(figsize=(8, 8))
        ax4.pie(category_sales['price_at_transaction'], labels=category_sales['category'], autopct='%1.1f%%', colors=sns.color_palette('pastel'))
        st.pyplot(fig4)

with tab3:
    st.subheader("Customer & Operational Insights")
    
    # AOV by Day of Week
    st.markdown("**Average Order Value by Day of Week**")
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    aov_by_day = df_trans_filtered.groupby('day_name')['total_amount'].mean().reindex(days_order).reset_index()
    
    fig5, ax5 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=aov_by_day, x='day_name', y='total_amount', palette="coolwarm", ax=ax5, hue='day_name', legend=False)
    ax5.set_xlabel("Day of Week")
    ax5.set_ylabel("Average Order Value ($)")
    st.pyplot(fig5)

# --- Raw Data ---
with st.expander("View Raw Data"):
    st.subheader("Recent Transactions")
    st.dataframe(df_trans_filtered.sort_values(by='transaction_date', ascending=False).head(50))
