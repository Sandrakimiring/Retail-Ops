"""
Preprocessing Script for Retail Operations
Loads raw retail CSVs and produces a clean daily KPI table.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuration
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
OUTPUT_FILE = "kpi_daily.csv"

def load_raw_data():
    """Load all raw CSV files."""
    print("Loading raw data files...")
    
    sales_df = pd.read_csv(f"{RAW_DATA_DIR}/sales.csv")
    print(f"  Loaded sales: {len(sales_df):,} records")
    
    inventory_df = pd.read_csv(f"{RAW_DATA_DIR}/inventory.csv")
    print(f"  Loaded inventory: {len(inventory_df):,} records")
    
    products_df = pd.read_csv(f"{RAW_DATA_DIR}/products.csv")
    print(f"  Loaded products: {len(products_df):,} records")
    
    stores_df = pd.read_csv(f"{RAW_DATA_DIR}/stores.csv")
    print(f"  Loaded stores: {len(stores_df):,} records")
    
    return sales_df, inventory_df, products_df, stores_df

def merge_data(sales_df, inventory_df, products_df, stores_df):
    """Merge all data sources together."""
    print("\nMerging data sources...")
    
    # Merge sales with products to get cost_price
    merged_df = sales_df.merge(
        products_df[['product_id', 'cost_price']],
        on='product_id',
        how='left'
    )
    
    # Merge with inventory to get stockout information
    merged_df = merged_df.merge(
        inventory_df[['date', 'store_id', 'product_id', 'stockout_flag']],
        on=['date', 'store_id', 'product_id'],
        how='left'
    )
    
    # Merge with stores (optional, but good for completeness)
    merged_df = merged_df.merge(
        stores_df,
        on='store_id',
        how='left'
    )
    
    print(f"  Merged dataset: {len(merged_df):,} records")
    
    # Check for missing values
    missing_cost = merged_df['cost_price'].isna().sum()
    missing_stockout = merged_df['stockout_flag'].isna().sum()
    
    if missing_cost > 0:
        print(f"  Warning: {missing_cost} records missing cost_price")
    if missing_stockout > 0:
        print(f"  Warning: {missing_stockout} records missing stockout_flag")
    
    return merged_df

def calculate_kpis(merged_df):
    """Calculate daily KPIs aggregated by store and category."""
    print("\nCalculating daily KPIs...")
    
    # Calculate cost for each transaction
    merged_df['cost'] = merged_df['units_sold'] * merged_df['cost_price']
    
    # Aggregate to daily level by store and category
    kpi_df = merged_df.groupby(['date', 'store_id', 'category']).agg({
        'revenue': 'sum',  # total_revenue
        'cost': 'sum',     # total_cost
        'stockout_flag': 'mean'  # stockout_rate (percentage)
    }).reset_index()
    
    # Rename columns
    kpi_df.rename(columns={
        'revenue': 'total_revenue',
        'stockout_flag': 'stockout_rate'
    }, inplace=True)
    
    # Calculate gross_margin = (revenue - cost) / revenue
    # Handle division by zero
    kpi_df['gross_margin'] = np.where(
        kpi_df['total_revenue'] > 0,
        (kpi_df['total_revenue'] - kpi_df['cost']) / kpi_df['total_revenue'],
        np.nan
    )
    
    # Round numeric columns
    kpi_df['total_revenue'] = kpi_df['total_revenue'].round(2)
    kpi_df['gross_margin'] = kpi_df['gross_margin'].round(4)
    kpi_df['stockout_rate'] = kpi_df['stockout_rate'].round(4)
    
    # Drop cost column (not needed in final output)
    kpi_df = kpi_df.drop(columns=['cost'])
    
    # Ensure date is datetime type for proper sorting
    kpi_df['date'] = pd.to_datetime(kpi_df['date'])
    
    # Sort by date, store_id, and category
    kpi_df = kpi_df.sort_values(['date', 'store_id', 'category']).reset_index(drop=True)
    
    # Convert date back to string format for CSV output
    kpi_df['date'] = kpi_df['date'].dt.strftime('%Y-%m-%d')
    
    print(f"  Generated {len(kpi_df):,} daily KPI records")
    print(f"  Date range: {kpi_df['date'].min()} to {kpi_df['date'].max()}")
    print(f"  Stores: {kpi_df['store_id'].nunique()}")
    print(f"  Categories: {kpi_df['category'].nunique()}")
    
    return kpi_df

def save_processed_data(kpi_df, output_path):
    """Save processed data to CSV."""
    print(f"\nSaving processed data to {output_path}...")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    kpi_df.to_csv(output_path, index=False)
    print(f"  Saved: {output_path} ({len(kpi_df):,} records)")
    
    # Display summary statistics
    print("\n" + "="*50)
    print("KPI SUMMARY STATISTICS")
    print("="*50)
    print(f"Total revenue: ${kpi_df['total_revenue'].sum():,.2f}")
    print(f"Average daily revenue: ${kpi_df['total_revenue'].mean():,.2f}")
    print(f"Average gross margin: {kpi_df['gross_margin'].mean():.2%}")
    print(f"Average stockout rate: {kpi_df['stockout_rate'].mean():.2%}")
    print("="*50)

def main():
    """Main function to process raw data and generate KPI table."""
    print("="*50)
    print("RETAIL DATA PREPROCESSING")
    print("="*50)
    
    # Load raw data
    sales_df, inventory_df, products_df, stores_df = load_raw_data()
    
    # Merge data
    merged_df = merge_data(sales_df, inventory_df, products_df, stores_df)
    
    # Calculate KPIs
    kpi_df = calculate_kpis(merged_df)
    
    # Save processed data
    output_path = f"{PROCESSED_DATA_DIR}/{OUTPUT_FILE}"
    save_processed_data(kpi_df, output_path)
    
    print("\nPreprocessing complete!")

if __name__ == "__main__":
    main()
