import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

print("Loading data from database...")
conn = sqlite3.connect('Data/olist.db')

# Load all tables
orders    = pd.read_sql("SELECT * FROM orders", conn)
items     = pd.read_sql("SELECT * FROM order_items", conn)
customers = pd.read_sql("SELECT * FROM customers", conn)
reviews   = pd.read_sql("SELECT * FROM reviews", conn)
products  = pd.read_sql("SELECT * FROM products", conn)
sellers   = pd.read_sql("SELECT * FROM sellers", conn)
categories= pd.read_sql("SELECT * FROM categories", conn)
payments  = pd.read_sql("SELECT order_id, payment_type FROM payments", conn)
conn.close()
print("✓ All tables loaded")

# ================================================
# STEP 1 - Fix date columns
# ================================================
date_cols = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]
for col in date_cols:
    orders[col] = pd.to_datetime(orders[col])
print("✓ Dates fixed")

# ================================================
# STEP 2 - Add useful columns
# ================================================
# How many days did delivery take?
orders['delivery_days'] = (
    orders['order_delivered_customer_date'] -
    orders['order_purchase_timestamp']
).dt.days

# Was the order delivered late?
orders['is_late'] = (
    orders['order_delivered_customer_date'] >
    orders['order_estimated_delivery_date']
).astype(int)

# Month and year columns
orders['order_month'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
orders['order_year']  = orders['order_purchase_timestamp'].dt.year
orders['order_dow']   = orders['order_purchase_timestamp'].dt.day_name()
print("✓ New columns added")

# ================================================
# STEP 3 - Merge all tables together
# ================================================
df = orders.merge(items,      on='order_id',    how='left')
df = df.merge(customers,      on='customer_id', how='left')
df = df.merge(reviews[['order_id','review_score']], on='order_id', how='left')
df = df.merge(products[['product_id','product_category_name']], on='product_id', how='left')
df = df.merge(categories,     on='product_category_name', how='left')
df = df.merge(payments,       on='order_id',    how='left')

# Keep only delivered orders
df = df[df['order_status'] == 'delivered'].copy()
print(f"✓ All tables merged: {df.shape[0]} rows, {df.shape[1]} columns")

# ================================================
# STEP 4 - Save clean data
# ================================================
df.to_csv('Output/clean_data.csv', index=False)
print("✓ Clean data saved to Output/clean_data.csv")

# ================================================
# STEP 5 - Print the 5 key insights
# ================================================
print("")
print("=" * 50)
print("KEY INSIGHTS")
print("=" * 50)

# Insight 1 - Delivery delay vs review score
print("\n1. Avg delivery days by review score:")
insight1 = df.groupby('review_score')['delivery_days'].mean().round(1)
print(insight1)

# Insight 2 - Top 5 states by revenue
print("\n2. Top 5 states by revenue:")
insight2 = df.groupby('customer_state')['price'].sum().nlargest(5).round(2)
print(insight2)

# Insight 3 - Late delivery rate
late_rate = df['is_late'].mean() * 100
print(f"\n3. Late delivery rate: {late_rate:.1f}%")

# Insight 4 - Average order value by category
print("\n4. Top 5 categories by avg order value:")
insight4 = df.groupby('product_category_name_english')['price'].mean().nlargest(5).round(2)
print(insight4)

# Insight 5 - Monthly revenue trend
print("\n5. Revenue by year:")
insight5 = df.groupby('order_year')['price'].sum().round(2)
print(insight5)

# ================================================
# STEP 6 - Create and save 4 charts
# ================================================
print("\nGenerating charts...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('E-Commerce Sales Analytics - Key Insights', fontsize=16)

# Chart 1 - Delivery days vs review score
delay = df.groupby('review_score')['delivery_days'].mean().round(1)
axes[0,0].bar(delay.index, delay.values, color='#185FA5')
axes[0,0].set_title('Avg Delivery Days by Review Score')
axes[0,0].set_xlabel('Review Score (1=Worst, 5=Best)')
axes[0,0].set_ylabel('Avg Days')

# Chart 2 - Top 10 states by revenue
state_rev = df.groupby('customer_state')['price'].sum().nlargest(10)
axes[0,1].barh(state_rev.index, state_rev.values, color='#1D9E75')
axes[0,1].set_title('Top 10 States by Revenue')
axes[0,1].set_xlabel('Revenue (R$)')

# Chart 3 - Monthly revenue trend
monthly = df.groupby('order_month')['price'].sum()
axes[1,0].plot(monthly.index, monthly.values, color='#534AB7', linewidth=2)
axes[1,0].set_title('Monthly Revenue Trend')
axes[1,0].set_xlabel('Month')
axes[1,0].set_ylabel('Revenue (R$)')
axes[1,0].tick_params(axis='x', rotation=45)

# Chart 4 - Top 10 categories by revenue
cat_rev = df.groupby('product_category_name_english')['price'].sum().nlargest(10)
axes[1,1].bar(cat_rev.index, cat_rev.values, color='#BA7517')
axes[1,1].set_title('Top 10 Categories by Revenue')
axes[1,1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('Output/eda_charts.png', dpi=150, bbox_inches='tight')
print("✓ Charts saved to Output/eda_charts.png")
print("")
print("clean.py completed successfully!")