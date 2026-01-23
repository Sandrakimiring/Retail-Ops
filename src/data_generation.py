"""
Data Generation Script for Retail Operations
Generates realistic synthetic retail data with 12 months of daily transactions.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_STORES = 10
NUM_PRODUCTS = 30
NUM_CATEGORIES = 5
NUM_SUPPLIERS = 3
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)

# Create output directory if it doesn't exist
OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_stores():
    """Generate store master data."""
    regions = ["North", "South", "East", "West", "Central"]
    store_types = ["Supermarket", "Wholesale", "Minimart"]
   
    stores = []
    for store_id in range(1, NUM_STORES + 1):
        stores.append({
            "store_id": store_id,
            "region": random.choice(regions),
            "store_type": random.choice(store_types)
        })
   
    return pd.DataFrame(stores)

def generate_products():
    """Generate product master data."""
    categories = [f"Category_{i+1}" for i in range(NUM_CATEGORIES)]
   
    products = []
    for product_id in range(1, NUM_PRODUCTS + 1):
        products.append({
            "product_id": product_id,
            "category": random.choice(categories),
            "supplier_id": random.randint(1, NUM_SUPPLIERS),
            "cost_price": round(np.random.uniform(5, 100), 2)
        })
   
    return pd.DataFrame(products)

def generate_dates():
    """Generate all dates for the year."""
    dates = []
    current_date = START_DATE
    while current_date <= END_DATE:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates

def generate_sales_data(dates, stores_df, products_df):
    """Generate sales transactions with realistic patterns."""
    sales_records = []
   
    for date in dates:
        is_weekend = date.weekday() >= 5  # Saturday = 5, Sunday = 6
        is_promotion_day = random.random() < 0.15  # 15% chance of promotion
       
        for store_id in range(1, NUM_STORES + 1):
            for product_id in range(1, NUM_PRODUCTS + 1):
                # Base sales volume
                base_units = np.random.poisson(lam=10)
               
                # Weekend boost (30-50% increase)
                if is_weekend:
                    base_units = int(base_units * np.random.uniform(1.3, 1.5))
               
                # Store type effect
                store_type = stores_df[stores_df['store_id'] == store_id]['store_type'].values[0]
                if store_type == "Minimart":
                    base_units = int(base_units * np.random.uniform(1.2, 1.4))
                elif store_type == "Wholesale":
                    base_units = int(base_units * np.random.uniform(0.7, 0.9))
               
                # Check for stockout (5% chance)
                stockout = random.random() < 0.05
                if stockout:
                    base_units = max(0, int(base_units * np.random.uniform(0.1, 0.3)))
               
                # Skip if no units sold
                if base_units == 0:
                    continue
               
                # Get product info
                product_info = products_df[products_df['product_id'] == product_id].iloc[0]
                category = product_info['category']
                cost_price = product_info['cost_price']
               
                # Calculate price (markup of 30-60% on cost)
                markup = np.random.uniform(1.3, 1.6)
                price = round(cost_price * markup, 2)
               
                # Discount rate
                if is_promotion_day and random.random() < 0.4:  # 40% of products on promotion day
                    discount_rate = round(np.random.uniform(0.15, 0.35), 3)  # 15-35% discount
                else:
                    discount_rate = round(np.random.uniform(0.0, 0.1), 3)  # 0-10% regular discount
               
                # Calculate revenue: units_sold * price * (1 - discount_rate)
                revenue = round(base_units * price * (1 - discount_rate), 2)
               
                sales_records.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "store_id": store_id,
                    "product_id": product_id,
                    "category": category,
                    "units_sold": base_units,
                    "price": price,
                    "discount_rate": discount_rate,
                    "revenue": revenue
                })
   
    return pd.DataFrame(sales_records)

def generate_inventory_data(dates, stores_df, products_df, sales_df):
    """Generate inventory data with stockouts."""
    inventory_records = []
   
    # Group sales by date, store, and product to estimate stock levels
    sales_grouped = sales_df.groupby(['date', 'store_id', 'product_id'])['units_sold'].sum().reset_index()
   
    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
       
        for store_id in range(1, NUM_STORES + 1):
            for product_id in range(1, NUM_PRODUCTS + 1):
                # Get sales for this product/store/date
                sales_for_item = sales_grouped[
                    (sales_grouped['date'] == date_str) &
                    (sales_grouped['store_id'] == store_id) &
                    (sales_grouped['product_id'] == product_id)
                ]
               
                if len(sales_for_item) > 0:
                    units_sold = sales_for_item['units_sold'].values[0]
                    # Stock on hand is typically 2-5x daily sales (with some randomness)
                    base_stock = units_sold * np.random.uniform(2, 5)
                    # Add some variation
                    stock_on_hand = max(0, int(base_stock + np.random.normal(0, base_stock * 0.2)))
                else:
                    # No sales, but still have some stock
                    stock_on_hand = int(np.random.uniform(10, 50))
               
                # Stockout flag (stock < 5 units)
                stockout_flag = 1 if stock_on_hand < 5 else 0
               
                inventory_records.append({
                    "date": date_str,
                    "store_id": store_id,
                    "product_id": product_id,
                    "stock_on_hand": stock_on_hand,
                    "stockout_flag": stockout_flag
                })
   
    return pd.DataFrame(inventory_records)

def main():
    """Main function to generate all data files."""
    print("Generating retail data...")
    print(f"Period: {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')}")
    print(f"Stores: {NUM_STORES}, Products: {NUM_PRODUCTS}, Categories: {NUM_CATEGORIES}, Suppliers: {NUM_SUPPLIERS}")
   
    # Generate master data
    print("\nGenerating master data...")
    stores_df = generate_stores()
    products_df = generate_products()
   
    # Generate dates
    dates = generate_dates()
    print(f"Generating data for {len(dates)} days...")
   
    # Generate sales data
    print("Generating sales data...")
    sales_df = generate_sales_data(dates, stores_df, products_df)
    print(f"Generated {len(sales_df):,} sales records")
   
    # Generate inventory data
    print("Generating inventory data...")
    inventory_df = generate_inventory_data(dates, stores_df, products_df, sales_df)
    print(f"Generated {len(inventory_df):,} inventory records")
   
    # Save to CSV files
    print("\nSaving data to CSV files...")
    stores_df.to_csv(f"{OUTPUT_DIR}/stores.csv", index=False)
    print(f"Saved: {OUTPUT_DIR}/stores.csv ({len(stores_df)} records)")
   
    products_df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
    print(f"Saved: {OUTPUT_DIR}/products.csv ({len(products_df)} records)")
   
    sales_df.to_csv(f"{OUTPUT_DIR}/sales.csv", index=False)
    print(f"Saved: {OUTPUT_DIR}/sales.csv ({len(sales_df):,} records)")
   
    inventory_df.to_csv(f"{OUTPUT_DIR}/inventory.csv", index=False)
    print(f"Saved: {OUTPUT_DIR}/inventory.csv ({len(inventory_df):,} records)")
   
    # Verify revenue calculation
    print("\nVerifying data integrity...")
    sales_df['calculated_revenue'] = sales_df['units_sold'] * sales_df['price'] * (1 - sales_df['discount_rate'])
    sales_df['calculated_revenue'] = sales_df['calculated_revenue'].round(2)
    revenue_diff = (sales_df['revenue'] - sales_df['calculated_revenue']).abs()
    max_diff = revenue_diff.max()
   
    if max_diff < 0.01:  # Allow for floating point precision
        print("✓ Revenue calculation verified (all values match)")
    else:
        print(f"⚠ Warning: Revenue calculation differences found (max diff: {max_diff})")
   
    # Print summary statistics
    print("\n" + "="*50)
    print("DATA GENERATION SUMMARY")
    print("="*50)
    print(f"Total sales records: {len(sales_df):,}")
    print(f"Total revenue: ${sales_df['revenue'].sum():,.2f}")
    print(f"Average daily sales: {len(sales_df) / len(dates):.1f} records")
    print(f"Weekend sales boost: Active")
    print(f"Promotions: ~15% of days")
    print(f"Stockouts: ~5% of product-store-days")
    print("="*50)
    print("\nData generation complete!")

if __name__ == "__main__":
    main()
