import pandas as pd
import sqlite3

# Connect to database (creates olist.db automatically)
conn = sqlite3.connect('Data/olist.db')

# List of all 8 files to load
files = {
    'orders':      'Data/olist_orders_dataset.csv',
    'order_items': 'Data/olist_order_items_dataset.csv',
    'customers':   'Data/olist_customers_dataset.csv',
    'products':    'Data/olist_products_dataset.csv',
    'sellers':     'Data/olist_sellers_dataset.csv',
    'reviews':     'Data/olist_order_reviews_dataset.csv',
    'payments':    'Data/olist_order_payments_dataset.csv',
    'categories':  'Data/product_category_name_translation.csv'
}

# Load each file into the database
for table_name, file_path in files.items():
    df = pd.read_csv(file_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f'✓ Loaded {table_name}: {len(df)} rows')

conn.close()
print('')
print('All 8 tables loaded successfully!')