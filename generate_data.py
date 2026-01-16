import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta
import numpy as np

# Initialize Faker
fake = Faker()

# Database Connection
conn = sqlite3.connect('coffee_shop.db')
cursor = conn.cursor()

# Create Tables
cursor.executescript('''
    DROP TABLE IF EXISTS transaction_items;
    DROP TABLE IF EXISTS transactions;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS products;

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        join_date TEXT
    );

    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        transaction_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    );

    CREATE TABLE transaction_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_at_transaction REAL NOT NULL,
        FOREIGN KEY(transaction_id) REFERENCES transactions(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    );
''')

# 1. Populate Products
products = [
    ('Espresso', 'Coffee', 2.50),
    ('Double Espresso', 'Coffee', 3.00),
    ('Latte', 'Coffee', 4.00),
    ('Cappuccino', 'Coffee', 4.00),
    ('Americano', 'Coffee', 3.00),
    ('Mocha', 'Coffee', 4.50),
    ('Caramel Macchiato', 'Coffee', 4.75),
    ('Cold Brew', 'Coffee', 3.75),
    ('Green Tea', 'Tea', 2.75),
    ('Earl Grey', 'Tea', 2.75),
    ('Chai Latte', 'Tea', 4.25),
    ('Hot Chocolate', 'Beverage', 3.50),
    ('Croissant', 'Bakery', 2.75),
    ('Chocolate Croissant', 'Bakery', 3.25),
    ('Blueberry Muffin', 'Bakery', 3.00),
    ('Bagel', 'Bakery', 2.00),
    ('Ham & Cheese Sandwich', 'Food', 6.50),
    ('Turkey Club', 'Food', 7.00),
    ('Avocado Toast', 'Food', 5.50)
]

cursor.executemany('INSERT INTO products (name, category, price) VALUES (?, ?, ?)', products)
conn.commit()

# Get product IDs map for easy access
cursor.execute('SELECT id, price FROM products')
product_map = {row[0]: row[1] for row in cursor.fetchall()}
product_ids = list(product_map.keys())

# 2. Populate Customers
num_customers = 150
customers = []
for _ in range(num_customers):
    join_date = fake.date_between(start_date='-1y', end_date='today')
    customers.append((fake.name(), fake.email(), join_date))

cursor.executemany('INSERT INTO customers (name, email, join_date) VALUES (?, ?, ?)', customers)
conn.commit()

# 3. Generate Transactions
# Let's simulate data for the last 90 days
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
num_transactions = 2000

print(f"Generating {num_transactions} transactions from {start_date.date()} to {end_date.date()}...")

# Weights for time of day (Morning rush 7-10, Lunch 12-2, Afternoon 2-5, Evening 5-7)
hours = list(range(7, 20)) # 7 AM to 7 PM
hour_weights = [0.15, 0.2, 0.15, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05, 0.02, 0.02, 0.03, 0.03]
# Normalize weights
hour_weights = [w/sum(hour_weights) for w in hour_weights]

for _ in range(num_transactions):
    # Random date
    days_offset = random.randint(0, 90)
    trans_date = start_date + timedelta(days=days_offset)
    
    # Random time based on weights
    hour = np.random.choice(hours, p=hour_weights)
    minute = random.randint(0, 59)
    trans_datetime = trans_date.replace(hour=hour, minute=minute, second=random.randint(0,59))
    
    # Customer (70% chance of being a registered customer, 30% guest/null)
    customer_id = random.randint(1, num_customers) if random.random() < 0.7 else None
    
    # Generate Items
    num_items = random.choices([1, 2, 3, 4, 5], weights=[0.5, 0.3, 0.1, 0.05, 0.05])[0]
    selected_products = random.choices(product_ids, k=num_items)
    
    transaction_total = 0
    items_to_insert = []
    
    # Create Transaction Record first to get ID
    cursor.execute('INSERT INTO transactions (customer_id, transaction_date, total_amount) VALUES (?, ?, ?)', 
                   (customer_id, trans_datetime.strftime("%Y-%m-%d %H:%M:%S"), 0))
    transaction_id = cursor.lastrowid
    
    for pid in selected_products:
        qty = 1 # Keeping simple for now, mostly 1 of each item type per transaction line
        price = product_map[pid]
        transaction_total += price * qty
        items_to_insert.append((transaction_id, pid, qty, price))
        
    # Update total amount
    cursor.execute('UPDATE transactions SET total_amount = ? WHERE id = ?', (transaction_total, transaction_id))
    
    # Insert items
    cursor.executemany('INSERT INTO transaction_items (transaction_id, product_id, quantity, price_at_transaction) VALUES (?, ?, ?, ?)', items_to_insert)

conn.commit()
conn.close()
print("Database generation complete.")
