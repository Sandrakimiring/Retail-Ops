"""
Root Cause Analysis Script for Retail Operations
Explains detected operational issues by identifying contributing drivers.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os
from datetime import datetime, timedelta

# Configuration
PROCESSED_DATA_DIR = "data/processed"
RAW_DATA_DIR = "data/raw"
ANOMALIES_FILE = "anomalies.csv"
OUTPUT_FILE = "root_causes.csv"

# Analysis parameters
BASELINE_PERIOD_DAYS = 30  # Days before anomaly to use as baseline
MIN_SAMPLES_PER_PERIOD = 10  # Minimum samples needed for analysis

def load_data():
    """Load anomalies and raw data."""
    print("Loading data...")
    
    # Load anomalies
    anomalies_df = pd.read_csv(f"{PROCESSED_DATA_DIR}/{ANOMALIES_FILE}")
    anomalies_df['start_date'] = pd.to_datetime(anomalies_df['start_date'])
    anomalies_df['end_date'] = pd.to_datetime(anomalies_df['end_date'])
    
    # Load raw data
    sales_df = pd.read_csv(f"{RAW_DATA_DIR}/sales.csv")
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    
    inventory_df = pd.read_csv(f"{RAW_DATA_DIR}/inventory.csv")
    inventory_df['date'] = pd.to_datetime(inventory_df['date'])
    
    products_df = pd.read_csv(f"{RAW_DATA_DIR}/products.csv")
    stores_df = pd.read_csv(f"{RAW_DATA_DIR}/stores.csv")
    
    print(f"  Loaded {len(anomalies_df)} anomalies")
    print(f"  Loaded {len(sales_df):,} sales records")
    print(f"  Loaded {len(inventory_df):,} inventory records")
    
    return anomalies_df, sales_df, inventory_df, products_df, stores_df

def prepare_feature_data(sales_df, inventory_df, products_df, stores_df):
    """Prepare merged feature dataset."""
    print("\nPreparing feature data...")
    
    # Merge sales with products to get supplier_id
    sales_with_products = sales_df.merge(
        products_df[['product_id', 'supplier_id', 'cost_price']],
        on='product_id',
        how='left'
    )
    
    # Merge with stores to get store_type
    sales_with_stores = sales_with_products.merge(
        stores_df[['store_id', 'store_type', 'region']],
        on='store_id',
        how='left'
    )
    
    # Merge with inventory to get stock_on_hand
    sales_with_inventory = sales_with_stores.merge(
        inventory_df[['date', 'store_id', 'product_id', 'stock_on_hand']],
        on=['date', 'store_id', 'product_id'],
        how='left'
    )
    
    print(f"  Merged dataset: {len(sales_with_inventory):,} records")
    
    return sales_with_inventory

def extract_features_for_period(feature_df, store_id, category, start_date, end_date):
    """Extract aggregated features for a specific period, store, and category."""
    # Filter data
    period_data = feature_df[
        (feature_df['store_id'] == store_id) &
        (feature_df['category'] == category) &
        (feature_df['date'] >= start_date) &
        (feature_df['date'] <= end_date)
    ].copy()
    
    if len(period_data) < MIN_SAMPLES_PER_PERIOD:
        return None
    
    # Aggregate features
    features = {
        # Categorical features (mode/most common)
        'supplier_id': period_data['supplier_id'].mode()[0] if len(period_data['supplier_id'].mode()) > 0 else period_data['supplier_id'].iloc[0],
        'store_type': period_data['store_type'].mode()[0] if len(period_data['store_type'].mode()) > 0 else period_data['store_type'].iloc[0],
        'region': period_data['region'].mode()[0] if len(period_data['region'].mode()) > 0 else period_data['region'].iloc[0],
        
        # Numerical features (aggregated)
        'avg_discount_rate': period_data['discount_rate'].mean(),
        'max_discount_rate': period_data['discount_rate'].max(),
        'avg_stock_on_hand': period_data['stock_on_hand'].mean() if period_data['stock_on_hand'].notna().any() else 0,
        'min_stock_on_hand': period_data['stock_on_hand'].min() if period_data['stock_on_hand'].notna().any() else 0,
        'avg_price': period_data['price'].mean(),
        'avg_units_sold': period_data['units_sold'].mean(),
        'total_units_sold': period_data['units_sold'].sum(),
        'avg_cost_price': period_data['cost_price'].mean(),
        
        # Additional derived features
        'discount_frequency': (period_data['discount_rate'] > 0.1).sum() / len(period_data),  # % of transactions with >10% discount
        'low_stock_frequency': (period_data['stock_on_hand'] < 10).sum() / len(period_data) if period_data['stock_on_hand'].notna().any() else 0,
        'avg_markup': ((period_data['price'] - period_data['cost_price']) / period_data['cost_price']).mean(),
    }
    
    return features

def analyze_anomaly_root_cause(anomaly_row, feature_df):
    """Analyze root cause for a single anomaly."""
    store_id = anomaly_row['store_id']
    category = anomaly_row['category']
    start_date = anomaly_row['start_date']
    end_date = anomaly_row['end_date']
    
    # Define baseline period (before anomaly)
    baseline_end = start_date - timedelta(days=1)
    baseline_start = baseline_end - timedelta(days=BASELINE_PERIOD_DAYS)
    
    # Extract features for both periods
    baseline_features = extract_features_for_period(
        feature_df, store_id, category, baseline_start, baseline_end
    )
    anomaly_features = extract_features_for_period(
        feature_df, store_id, category, start_date, end_date
    )
    
    if baseline_features is None or anomaly_features is None:
        return None
    
    # Create comparison dataset
    # We'll create multiple samples by aggregating daily data
    baseline_data = feature_df[
        (feature_df['store_id'] == store_id) &
        (feature_df['category'] == category) &
        (feature_df['date'] >= baseline_start) &
        (feature_df['date'] <= baseline_end)
    ]
    
    anomaly_data = feature_df[
        (feature_df['store_id'] == store_id) &
        (feature_df['category'] == category) &
        (feature_df['date'] >= start_date) &
        (feature_df['date'] <= end_date)
    ]
    
    if len(baseline_data) < MIN_SAMPLES_PER_PERIOD or len(anomaly_data) < MIN_SAMPLES_PER_PERIOD:
        return None
    
    # Aggregate by day for more samples - use simpler aggregation
    def get_mode(x):
        if len(x) == 0:
            return None
        mode_vals = x.mode()
        if len(mode_vals) > 0:
            return mode_vals[0]
        else:
            return x.iloc[0]
    
    baseline_daily = baseline_data.groupby('date').agg({
        'supplier_id': get_mode,
        'store_type': get_mode,
        'region': get_mode,
        'discount_rate': 'mean',
        'stock_on_hand': 'mean',
        'price': 'mean',
        'units_sold': 'sum',
        'cost_price': 'mean'
    }).reset_index()
    
    anomaly_daily = anomaly_data.groupby('date').agg({
        'supplier_id': get_mode,
        'store_type': get_mode,
        'region': get_mode,
        'discount_rate': 'mean',
        'stock_on_hand': 'mean',
        'price': 'mean',
        'units_sold': 'sum',
        'cost_price': 'mean'
    }).reset_index()
    
    # Add derived features - calculate more efficiently
    baseline_daily['discount_frequency'] = baseline_data.groupby('date')['discount_rate'].apply(
        lambda x: (x > 0.1).sum() / len(x) if len(x) > 0 else 0
    ).values
    anomaly_daily['discount_frequency'] = anomaly_data.groupby('date')['discount_rate'].apply(
        lambda x: (x > 0.1).sum() / len(x) if len(x) > 0 else 0
    ).values
    
    baseline_daily['low_stock_frequency'] = baseline_data.groupby('date')['stock_on_hand'].apply(
        lambda x: (x < 10).sum() / len(x) if len(x) > 0 and x.notna().any() else 0
    ).values
    anomaly_daily['low_stock_frequency'] = anomaly_data.groupby('date')['stock_on_hand'].apply(
        lambda x: (x < 10).sum() / len(x) if len(x) > 0 and x.notna().any() else 0
    ).values
    
    # Calculate markup safely
    baseline_daily['avg_markup'] = np.where(
        baseline_daily['cost_price'] > 0,
        (baseline_daily['price'] - baseline_daily['cost_price']) / baseline_daily['cost_price'],
        0
    )
    anomaly_daily['avg_markup'] = np.where(
        anomaly_daily['cost_price'] > 0,
        (anomaly_daily['price'] - anomaly_daily['cost_price']) / anomaly_daily['cost_price'],
        0
    )
    
    # Prepare feature columns
    feature_cols = ['supplier_id', 'store_type', 'region', 'discount_rate', 
                    'stock_on_hand', 'price', 'units_sold', 'cost_price',
                    'discount_frequency', 'low_stock_frequency', 'avg_markup']
    
    # Combine baseline and anomaly data
    baseline_daily['period'] = 0  # Baseline
    anomaly_daily['period'] = 1  # Anomaly
    
    combined_data = pd.concat([
        baseline_daily[feature_cols + ['period']],
        anomaly_daily[feature_cols + ['period']]
    ], ignore_index=True)
    
    # Handle missing values
    combined_data = combined_data.fillna(0)
    
    # Encode categorical variables
    le_supplier = LabelEncoder()
    le_store_type = LabelEncoder()
    le_region = LabelEncoder()
    
    combined_data['supplier_id_encoded'] = le_supplier.fit_transform(combined_data['supplier_id'].astype(str))
    combined_data['store_type_encoded'] = le_store_type.fit_transform(combined_data['store_type'].astype(str))
    combined_data['region_encoded'] = le_region.fit_transform(combined_data['region'].astype(str))
    
    # Prepare features for model
    model_features = ['supplier_id_encoded', 'store_type_encoded', 'region_encoded',
                     'discount_rate', 'stock_on_hand', 'price', 'units_sold', 
                     'cost_price', 'discount_frequency', 'low_stock_frequency', 'avg_markup']
    
    X = combined_data[model_features]
    y = combined_data['period']
    
    if len(X) < MIN_SAMPLES_PER_PERIOD * 2:
        return None
    
    # Train classifier
    try:
        clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42, n_jobs=-1)
        clf.fit(X, y)
        
        # Get feature importance
        feature_importance = pd.DataFrame({
            'feature': model_features,
            'importance': clf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Map back to original feature names
        feature_mapping = {
            'supplier_id_encoded': 'supplier_id',
            'store_type_encoded': 'store_type',
            'region_encoded': 'region'
        }
        
        feature_importance['feature'] = feature_importance['feature'].replace(feature_mapping)
        
        # Calculate change metrics
        baseline_means = baseline_daily[feature_cols].mean()
        anomaly_means = anomaly_daily[feature_cols].mean()
        
        changes = {}
        for col in feature_cols:
            if col in ['supplier_id', 'store_type', 'region']:
                # For categorical, check if mode changed
                baseline_mode = baseline_daily[col].mode()[0] if len(baseline_daily[col].mode()) > 0 else None
                anomaly_mode = anomaly_daily[col].mode()[0] if len(anomaly_daily[col].mode()) > 0 else None
                changes[col] = 'changed' if baseline_mode != anomaly_mode else 'unchanged'
            else:
                # For numerical, calculate percent change
                if baseline_means[col] != 0:
                    pct_change = ((anomaly_means[col] - baseline_means[col]) / baseline_means[col]) * 100
                    changes[col] = f"{pct_change:.1f}%"
                else:
                    changes[col] = "N/A"
        
        # Combine importance with changes
        result = {
            'anomaly_id': f"{store_id}_{category}_{start_date.strftime('%Y%m%d')}",
            'store_id': store_id,
            'category': category,
            'metric': anomaly_row['metric'],
            'severity': anomaly_row['severity'],
            'drivers': []
        }
        
        for idx, row in feature_importance.iterrows():
            feature_name = row['feature']
            importance = row['importance']
            change = changes.get(feature_name, 'N/A')
            
            result['drivers'].append({
                'driver': feature_name,
                'importance_score': importance,
                'change': change
            })
        
        return result
        
    except Exception as e:
        print(f"    Error analyzing anomaly {store_id}_{category}: {e}")
        return None

def analyze_all_anomalies(anomalies_df, feature_df):
    """Analyze root causes for all anomalies."""
    print("\nAnalyzing root causes...")
    
    # Limit to top anomalies by severity and impact (to avoid timeout)
    # Process critical and high severity first, then sample others
    priority_anomalies = anomalies_df[
        anomalies_df['severity'].isin(['critical', 'high'])
    ].copy()
    
    other_anomalies = anomalies_df[
        ~anomalies_df['severity'].isin(['critical', 'high'])
    ].copy()
    
    # Sample up to 20 medium/low severity anomalies
    if len(other_anomalies) > 20:
        other_anomalies = other_anomalies.nlargest(20, 'max_impact')
    
    anomalies_to_process = pd.concat([priority_anomalies, other_anomalies]).reset_index(drop=True)
    
    print(f"  Processing {len(anomalies_to_process)} anomalies "
          f"(prioritizing {len(priority_anomalies)} critical/high severity)")
    
    root_causes = []
    
    for idx, anomaly_row in anomalies_to_process.iterrows():
        print(f"  Processing anomaly {idx+1}/{len(anomalies_to_process)}: "
              f"Store {anomaly_row['store_id']}, {anomaly_row['category']}, "
              f"{anomaly_row['metric']}")
        
        result = analyze_anomaly_root_cause(anomaly_row, feature_df)
        
        if result:
            root_causes.append(result)
    
    print(f"\n  Analyzed {len(root_causes)} anomalies")
    
    return root_causes

def format_root_causes(root_causes):
    """Format root causes into a DataFrame."""
    formatted_results = []
    
    for root_cause in root_causes:
        for driver in root_cause['drivers']:
            formatted_results.append({
                'anomaly_id': root_cause['anomaly_id'],
                'store_id': root_cause['store_id'],
                'category': root_cause['category'],
                'metric': root_cause['metric'],
                'severity': root_cause['severity'],
                'driver': driver['driver'],
                'importance_score': driver['importance_score'],
                'change': driver['change']
            })
    
    df = pd.DataFrame(formatted_results)
    
    # Sort by anomaly_id and importance_score
    df = df.sort_values(['anomaly_id', 'importance_score'], ascending=[True, False])
    
    return df

def save_root_causes(root_causes_df, output_path):
    """Save root causes to CSV."""
    print(f"\nSaving root causes to {output_path}...")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Round importance scores
    root_causes_df['importance_score'] = root_causes_df['importance_score'].round(4)
    
    # Save to CSV
    root_causes_df.to_csv(output_path, index=False)
    print(f"  Saved: {output_path} ({len(root_causes_df)} records)")
    
    # Display summary statistics
    print("\n" + "="*50)
    print("ROOT CAUSE ANALYSIS SUMMARY")
    print("="*50)
    
    if len(root_causes_df) > 0:
        print(f"\nTotal driver records: {len(root_causes_df)}")
        print(f"Unique anomalies analyzed: {root_causes_df['anomaly_id'].nunique()}")
        
        print(f"\nTop 10 most important drivers across all anomalies:")
        top_drivers = root_causes_df.groupby('driver')['importance_score'].mean().sort_values(ascending=False).head(10)
        for driver, score in top_drivers.items():
            print(f"  {driver}: {score:.4f}")
        
        print(f"\nDriver frequency (how often each driver appears in top 3):")
        top3_drivers = root_causes_df.groupby('anomaly_id').head(3)
        driver_freq = top3_drivers['driver'].value_counts()
        for driver, count in driver_freq.head(10).items():
            print(f"  {driver}: {count} times")
    
    print("="*50)

def main():
    """Main function to analyze root causes."""
    print("="*50)
    print("ROOT CAUSE ANALYSIS")
    print("="*50)
    
    # Load data
    anomalies_df, sales_df, inventory_df, products_df, stores_df = load_data()
    
    # Prepare feature data
    feature_df = prepare_feature_data(sales_df, inventory_df, products_df, stores_df)
    
    # Analyze all anomalies
    root_causes = analyze_all_anomalies(anomalies_df, feature_df)
    
    # Format results
    root_causes_df = format_root_causes(root_causes)
    
    # Save results
    output_path = f"{PROCESSED_DATA_DIR}/{OUTPUT_FILE}"
    save_root_causes(root_causes_df, output_path)
    
    print("\nRoot cause analysis complete!")

if __name__ == "__main__":
    main()
