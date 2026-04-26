#!/usr/bin/env python
"""Quick data cleaning to generate cleaned CSV for pipeline."""
import pandas as pd
from pathlib import Path

base = Path(r'c:\Users\Admin\OneDrive\Documents\python\data for impact\404_Not_Found')
excel_file = base / 'data' / 'online_retail_II.xlsx'

print(f'Loading Excel from: {excel_file}')
df1 = pd.read_excel(excel_file, sheet_name='Year 2009-2010', engine='openpyxl')
df2 = pd.read_excel(excel_file, sheet_name='Year 2010-2011', engine='openpyxl')
df = pd.concat([df1, df2], ignore_index=True)
print(f'Loaded: {len(df):,} rows')

# Clean
df = df.dropna(subset=['Customer ID'])
df = df.drop_duplicates()
df['Customer ID'] = df['Customer ID'].astype(int).astype(str)  # Keep as string
if 'Description' in df.columns:
    df['Description'] = df['Description'].fillna('Unknown Product')
df['IsReturn'] = df['Quantity'] < 0
df['TotalValue'] = df['Quantity'] * df['Price']

# Date features
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Year'] = df['InvoiceDate'].dt.year
df['Month'] = df['InvoiceDate'].dt.month
df['Day'] = df['InvoiceDate'].dt.day
df['Hour'] = df['InvoiceDate'].dt.hour
df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
df['DayOfWeekName'] = df['InvoiceDate'].dt.day_name()
df['Quarter'] = df['InvoiceDate'].dt.quarter

# First purchase
customer_first = df.groupby('Customer ID')['InvoiceDate'].min().reset_index()
customer_first.columns = ['Customer ID', 'FirstPurchaseDate']
df = df.merge(customer_first, on='Customer ID', how='left')
df['CohortYear'] = df['FirstPurchaseDate'].dt.year
df['CohortMonth'] = df['FirstPurchaseDate'].dt.month
df['CohortMonthYear'] = df['FirstPurchaseDate'].dt.to_period('M').astype(str)

# Invoice type
df['InvoiceType'] = df['Invoice'].apply(lambda x: 'Cancellation' if str(x).startswith('C') else 'Sale')

# Product category
df['ProductCategory'] = df['Description'].apply(
    lambda x: 'Gift' if 'gift' in str(x).lower() else
    'Decoration' if any(w in str(x).lower() for w in ['decoration', 'ornament', 'light']) else
    'Kitchen' if any(w in str(x).lower() for w in ['mug', 'cup', 'plate', 'kitchen']) else
    'Other'
)

# Save
cleaned_dir = base / 'data' / 'cleaned'
cleaned_dir.mkdir(exist_ok=True)
output_file = cleaned_dir / 'online_retail_cleaned_full.csv'
df.to_csv(output_file, index=False)
print(f'Saved: {len(df):,} rows to {output_file}')
print(f'File size: {output_file.stat().st_size / (1024**2):.1f} MB')
