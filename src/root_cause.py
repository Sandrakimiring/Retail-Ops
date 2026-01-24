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
import json

# Get script directory to make paths relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # Go up one level from src/ to project root

# Configuration - use paths relative to project root
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data/processed")
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data/raw")
ANOMALIES_FILE = "anomalies.csv"
OUTPUT_FILE = "root_causes.csv"

# Debug logging function
def debug_log(location, message, data, hypothesis_id="A"):
    log_path = os.path.join(PROJECT_ROOT, ".cursor", "debug.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            log_entry = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Silently fail if logging fails

# Analysis parameters
BASELINE_PERIOD_DAYS = 30  # Days before anomaly to use as baseline
MIN_SAMPLES_PER_PERIOD = 10  # Minimum samples needed for analysis

def load_data():
    """Load anomalies and raw data."""
    print("Loading data...")
    
    # Load anomalies
    anomalies_path = os.path.join(PROCESSED_DATA_DIR, ANOMALIES_FILE)
    debug_log("root_cause.py:28", "Loading anomalies", {"path": anomalies_path, "exists": os.path.exists(anomalies_path)}, "C")
    anomalies_df = pd.read_csv(anomalies_path)
    anomalies_df['start_date'] = pd.to_datetime(anomalies_df['start_date'])
    anomalies_df['end_date'] = pd.to_datetime(anomalies_df['end_date'])
    
    # Load raw data
    sales_df = pd.read_csv(os.path.join(RAW_DATA_DIR, "sales.csv"))
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    
    inventory_df = pd.read_csv(os.path.join(RAW_DATA_DIR, "inventory.csv"))
    inventory_df['date'] = pd.to_datetime(inventory_df['date'])
    
    products_df = pd.read_csv(os.path.join(RAW_DATA_DIR, "products.csv"))
    stores_df = pd.read_csv(os.path.join(RAW_DATA_DIR, "stores.csv"))
    
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
    
    # Aggregate by day for more samples
    # Aggregate numerical columns first
    baseline_daily = baseline_data.groupby('date').agg({
        'discount_rate': 'mean',
        'stock_on_hand': 'mean',
        'price': 'mean',
        'units_sold': 'sum',
        'cost_price': 'mean'
    }).reset_index()
    
    # Add categorical columns using mode (aggregate separately to avoid concatenation)
    # Use a more robust mode function that ensures scalar return
    def get_mode_value(series):
        if len(series) == 0:
            return None
        mode_result = series.mode()
        if len(mode_result) > 0:
            val = mode_result.iloc[0]
            debug_log("root_cause.py:167", f"Mode for {series.name}", {"mode_value": str(val), "type": str(type(val)), "is_scalar": pd.api.types.is_scalar(val)}, "A")
            return val
        else:
            val = series.iloc[0]
            debug_log("root_cause.py:171", f"First value for {series.name}", {"first_value": str(val), "type": str(type(val))}, "A")
            return val
    
    for col in ['supplier_id', 'store_type', 'region']:
        mode_series = baseline_data.groupby('date')[col].apply(get_mode_value)
        debug_log("root_cause.py:175", f"Mode series for {col}", {"length": len(mode_series), "sample_values": mode_series.head(3).tolist() if len(mode_series) > 0 else [], "dtype": str(mode_series.dtype)}, "A")
        baseline_daily[col] = baseline_daily['date'].map(mode_series)
        debug_log("root_cause.py:177", f"After mapping {col}", {"sample_values": baseline_daily[col].head(3).tolist(), "dtype": str(baseline_daily[col].dtype)}, "A")
    
    # Same for anomaly data
    anomaly_daily = anomaly_data.groupby('date').agg({
        'discount_rate': 'mean',
        'stock_on_hand': 'mean',
        'price': 'mean',
        'units_sold': 'sum',
        'cost_price': 'mean'
    }).reset_index()
    
    for col in ['supplier_id', 'store_type', 'region']:
        mode_series = anomaly_data.groupby('date')[col].apply(get_mode_value)
        anomaly_daily[col] = anomaly_daily['date'].map(mode_series)
    
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
    
    # Handle missing values - only fill numerical columns with 0
    # Categorical columns should keep their values (they shouldn't have NaN if aggregation worked correctly)
    numerical_cols_for_fill = ['discount_rate', 'stock_on_hand', 'price', 'units_sold', 
                               'cost_price', 'discount_frequency', 'low_stock_frequency', 'avg_markup']
    for col in numerical_cols_for_fill:
        if col in combined_data.columns:
            combined_data[col] = combined_data[col].fillna(0)
    
    # For categorical columns, fill with mode if needed
    for col in ['supplier_id', 'store_type', 'region']:
        if col in combined_data.columns and combined_data[col].isna().any():
            mode_val = combined_data[col].mode()[0] if len(combined_data[col].mode()) > 0 else combined_data[col].iloc[0]
            combined_data[col] = combined_data[col].fillna(mode_val)
    
    # Encode categorical variables
    # Debug: Check values before encoding
    debug_log("root_cause.py:232", "Before encoding", {
        "supplier_id_sample": combined_data['supplier_id'].head(3).tolist(),
        "supplier_id_dtype": str(combined_data['supplier_id'].dtype),
        "store_type_sample": combined_data['store_type'].head(3).tolist(),
        "store_type_dtype": str(combined_data['store_type'].dtype),
        "region_sample": combined_data['region'].head(3).tolist(),
        "region_dtype": str(combined_data['region'].dtype)
    }, "B")
    
    le_supplier = LabelEncoder()
    le_store_type = LabelEncoder()
    le_region = LabelEncoder()
    
    # Convert to string and ensure we have scalar values
    supplier_str = combined_data['supplier_id'].astype(str)
    store_type_str = combined_data['store_type'].astype(str)
    region_str = combined_data['region'].astype(str)
    
    debug_log("root_cause.py:245", "After string conversion", {
        "supplier_str_sample": supplier_str.head(3).tolist(),
        "store_type_str_sample": store_type_str.head(3).tolist(),
        "region_str_sample": region_str.head(3).tolist()
    }, "B")
    
    try:
        combined_data['supplier_id_encoded'] = le_supplier.fit_transform(supplier_str)
        combined_data['store_type_encoded'] = le_store_type.fit_transform(store_type_str)
        combined_data['region_encoded'] = le_region.fit_transform(region_str)
        debug_log("root_cause.py:252", "Encoding successful", {}, "B")
    except Exception as e:
        debug_log("root_cause.py:254", "Encoding failed", {"error": str(e), "error_type": type(e).__name__}, "B")
        raise
    
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
        # Separate numerical and categorical columns
        categorical_cols = ['supplier_id', 'store_type', 'region']
        numerical_cols = [col for col in feature_cols if col not in categorical_cols]
        
        # Only calculate means for numerical columns
        baseline_means = baseline_daily[numerical_cols].mean() if len(numerical_cols) > 0 else pd.Series()
        anomaly_means = anomaly_daily[numerical_cols].mean() if len(numerical_cols) > 0 else pd.Series()
        
        changes = {}
        # Handle categorical columns
        for col in categorical_cols:
            baseline_mode = baseline_daily[col].mode()[0] if len(baseline_daily[col].mode()) > 0 else None
            anomaly_mode = anomaly_daily[col].mode()[0] if len(anomaly_daily[col].mode()) > 0 else None
            changes[col] = 'changed' if baseline_mode != anomaly_mode else 'unchanged'
        
        # Handle numerical columns
        for col in numerical_cols:
            if col in baseline_means.index and baseline_means[col] != 0:
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
    if len(root_causes) == 0:
        # Return empty DataFrame with expected columns if no root causes found
        return pd.DataFrame(columns=['anomaly_id', 'store_id', 'category', 'metric', 
                                     'severity', 'driver', 'importance_score', 'change'])
    
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
    output_path = os.path.join(PROCESSED_DATA_DIR, OUTPUT_FILE)
    save_root_causes(root_causes_df, output_path)
    
    print("\nRoot cause analysis complete!")

if __name__ == "__main__":
    main()
