# comprehensive_pandas_project.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# 1. Creating DataFrames and Series
# ----------------------------
data = {
    'OrderID': [1001, 1002, 1003, 1004, 1005, 1006],
    'Customer': ['Alice', 'Bob', 'Charlie', 'Alice', 'Bob', 'Charlie'],
    'Product': ['Laptop', 'Mouse', 'Keyboard', 'Mouse', 'Laptop', 'Keyboard'],
    'Quantity': [1, 3, 2, 1, 2, 1],
    'Price': [1000, 25, 50, 25, 1000, 50],
    'OrderDate': pd.to_datetime([
        '2025-01-05', '2025-01-06', '2025-01-07',
        '2025-02-01', '2025-02-05', '2025-02-07'
    ])
}

df = pd.DataFrame(data)
print("Initial DataFrame:\n", df)

# ----------------------------
# 2. Reading/Writing Files
# ----------------------------
df.to_csv('orders.csv', index=False)
df.to_excel('orders.xlsx', index=False)
df.to_json('orders.json', orient='records')

# Read files back
df_csv = pd.read_csv('orders.csv')
df_excel = pd.read_excel('orders.xlsx')
df_json = pd.read_json('orders.json')

# ----------------------------
# 3. Indexing and Selection
# ----------------------------
print(df['Customer'])          # Select column
print(df[['Customer', 'Product']])  # Select multiple columns
print(df.iloc[0])             # Select first row
print(df.loc[df['Quantity'] > 1])   # Filter rows

# ----------------------------
# 4. Data Cleaning
# ----------------------------
df.loc[6] = [1007, 'David', 'Laptop', np.nan, 1000, '2025-02-10']
print("\nWith Missing Quantity:\n", df)

# Fill missing values
df['Quantity'].fillna(1, inplace=True)

# Drop duplicates
df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
 # Add duplicate row
df = df.drop_duplicates()

# ----------------------------
# 5. Data Transformation
# ----------------------------
# Add Total column
df['Total'] = df['Quantity'] * df['Price']

# Using apply
df['Customer_Upper'] = df['Customer'].apply(lambda x: x.upper())

# Map example
df['ProductCategory'] = df['Product'].map({
    'Laptop': 'Electronics',
    'Mouse': 'Accessories',
    'Keyboard': 'Accessories'
})

# ----------------------------
# 6. Grouping and Aggregation
# ----------------------------
grouped = df.groupby('Customer').agg({
    'Quantity': 'sum',
    'Total': 'sum'
}).reset_index()
print("\nGrouped Data:\n", grouped)

# ----------------------------
# 7. Merging, Joining, Concatenation
# ----------------------------
# Another dataset
discounts = pd.DataFrame({
    'Customer': ['Alice', 'Bob', 'Charlie'],
    'Discount': [50, 25, 0]
})

merged = pd.merge(df, discounts, on='Customer', how='left')
print("\nMerged Data:\n", merged)

# ----------------------------
# 8. Pivot Tables
# ----------------------------
pivot = pd.pivot_table(df, index='Customer', columns='Product', values='Quantity', aggfunc='sum', fill_value=0)
print("\nPivot Table:\n", pivot)

# -------------