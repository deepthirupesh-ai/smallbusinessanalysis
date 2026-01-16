import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Plot Style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Database Connection
conn = sqlite3.connect('coffee_shop.db')

# Load Data
print("Loading data...")
df_trans = pd.read_sql_query("SELECT * FROM transactions", conn)
df_items = pd.read_sql_query("SELECT * FROM transaction_items", conn)
df_products = pd.read_sql_query("SELECT * FROM products", conn)
df_customers = pd.read_sql_query("SELECT * FROM customers", conn)

conn.close()

# Data Preprocessing
df_trans['transaction_date'] = pd.to_datetime(df_trans['transaction_date'])
df_trans['hour'] = df_trans['transaction_date'].dt.hour
df_trans['day_name'] = df_trans['transaction_date'].dt.day_name()
df_trans['date'] = df_trans['transaction_date'].dt.date

# Merge Items with Products for detailed analysis
df_full_items = df_items.merge(df_products, left_on='product_id', right_on='id', suffixes=('_item', '_prod'))
df_full_items = df_full_items.merge(df_trans[['id', 'transaction_date', 'hour', 'day_name']], left_on='transaction_id', right_on='id')

# --- Analysis 1: General Stats ---
total_revenue = df_trans['total_amount'].sum()
total_transactions = len(df_trans)
avg_transaction_value = df_trans['total_amount'].mean()

print(f"\n--- General Statistics ---")
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Transactions: {total_transactions}")
print(f"Average Transaction Value: ${avg_transaction_value:,.2f}")

# --- Analysis 2: Daily Sales Trend ---
daily_sales = df_trans.groupby('date')['total_amount'].sum().reset_index()

plt.figure(figsize=(14, 6))
sns.lineplot(data=daily_sales, x='date', y='total_amount', marker='o')
plt.title('Daily Revenue Trend')
plt.xlabel('Date')
plt.ylabel('Total Revenue ($)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('analysis_output/daily_sales_trend.png')
print("Saved daily_sales_trend.png")

# --- Analysis 3: Hourly Traffic (Heatmap or Bar) ---
hourly_sales = df_trans.groupby('hour')['id'].count().reset_index(name='transaction_count')

plt.figure(figsize=(10, 6))
sns.barplot(data=hourly_sales, x='hour', y='transaction_count', palette="viridis", hue='hour', legend=False)
plt.title('Busy Hours (Number of Transactions by Hour)')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Transactions')
plt.tight_layout()
plt.savefig('analysis_output/hourly_traffic.png')
print("Saved hourly_traffic.png")

# --- Analysis 4: Top Selling Products ---
top_products = df_full_items.groupby('name')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()

plt.figure(figsize=(12, 6))
sns.barplot(data=top_products, y='name', x='quantity', palette="magma", hue='name', legend=False)
plt.title('Top 10 Selling Products')
plt.xlabel('Quantity Sold')
plt.ylabel('Product Name')
plt.tight_layout()
plt.savefig('analysis_output/top_products.png')
print("Saved top_products.png")

# --- Analysis 5: Sales by Category ---
category_sales = df_full_items.groupby('category')['price_at_transaction'].sum().reset_index()

plt.figure(figsize=(8, 8))
plt.pie(category_sales['price_at_transaction'], labels=category_sales['category'], autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Revenue Share by Category')
plt.tight_layout()
plt.savefig('analysis_output/category_sales.png')
print("Saved category_sales.png")

# --- Analysis 6: Average Order Value by Day of Week ---
# Order days to ensure Monday-Sunday
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
aov_by_day = df_trans.groupby('day_name')['total_amount'].mean().reindex(days_order).reset_index()

plt.figure(figsize=(10, 6))
sns.barplot(data=aov_by_day, x='day_name', y='total_amount', palette="coolwarm", hue='day_name', legend=False)
plt.title('Average Order Value by Day of Week')
plt.xlabel('Day of Week')
plt.ylabel('Average Order Value ($)')
plt.tight_layout()
plt.savefig('analysis_output/aov_by_day.png')
print("Saved aov_by_day.png")

print("\nAnalysis Complete. Check the 'analysis_output' folder for visualizations.")
