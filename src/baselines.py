"""
Baselines Script for Retail Operations
Learns normal (healthy) behavior for each KPI using rolling windows and seasonality.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
from datetime import datetime

# Configuration
PROCESSED_DATA_DIR = "data/processed"
INPUT_FILE = "kpi_daily.csv"
OUTPUT_FILE = "baselines.csv"

# Baseline parameters
ROLLING_WINDOW_DAYS = 30  # Days for rolling statistics
BOUNDS_STD_MULTIPLIER = 2.0  # Standard deviations for bounds
MIN_DATA_POINTS = 7  # Minimum data points needed before computing baselines

def load_kpi_data():
    """Load daily KPI data."""
    print("Loading KPI data...")
    
    kpi_df = pd.read_csv(f"{PROCESSED_DATA_DIR}/{INPUT_FILE}")
    kpi_df['date'] = pd.to_datetime(kpi_df['date'])
    
    print(f"  Loaded {len(kpi_df):,} records")
    print(f"  Date range: {kpi_df['date'].min().date()} to {kpi_df['date'].max().date()}")
    print(f"  Stores: {kpi_df['store_id'].nunique()}")
    print(f"  Categories: {kpi_df['category'].nunique()}")
    
    return kpi_df

def add_time_features(df):
    """Add time-based features for seasonality detection."""
    df = df.copy()
    df['day_of_week'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Create a numeric day index for trend analysis
    df = df.sort_values(['store_id', 'category', 'date'])
    df['day_index'] = df.groupby(['store_id', 'category']).cumcount()
    
    return df

def calculate_rolling_baseline(series, window=ROLLING_WINDOW_DAYS):
    """Calculate rolling mean and std for baseline."""
    rolling_mean = series.rolling(window=window, min_periods=min(window//2, MIN_DATA_POINTS)).mean()
    rolling_std = series.rolling(window=window, min_periods=min(window//2, MIN_DATA_POINTS)).std()
    
    return rolling_mean, rolling_std

def calculate_trend(series, day_index):
    """Calculate linear trend using simple regression."""
    # Only use non-null values
    mask = ~(series.isna() | day_index.isna())
    if mask.sum() < MIN_DATA_POINTS:
        return pd.Series(np.nan, index=series.index)
    
    X = day_index[mask].values.reshape(-1, 1)
    y = series[mask].values
    
    try:
        model = LinearRegression()
        model.fit(X, y)
        trend = model.predict(day_index.values.reshape(-1, 1))
        return pd.Series(trend, index=series.index)
    except:
        return pd.Series(np.nan, index=series.index)

def calculate_seasonality_adjustment(df, kpi_col):
    """Calculate seasonality adjustments based on day of week and month."""
    # Calculate average by day of week
    dow_avg = df.groupby('day_of_week')[kpi_col].mean()
    overall_avg = df[kpi_col].mean()
    
    # Calculate average by month
    month_avg = df.groupby('month')[kpi_col].mean()
    
    # Create adjustment factors
    dow_adjustment = (dow_avg / overall_avg).to_dict()
    month_adjustment = (month_avg / overall_avg).to_dict()
    
    # Apply adjustments
    df['dow_factor'] = df['day_of_week'].map(dow_adjustment)
    df['month_factor'] = df['month'].map(month_adjustment)
    
    # Combined seasonality factor
    df['seasonality_factor'] = (df['dow_factor'] + df['month_factor']) / 2
    
    return df

def compute_baselines_for_group(group_df, kpi_name):
    """Compute baselines for a single store-category-KPI combination."""
    group_df = group_df.sort_values('date').reset_index(drop=True)
    
    kpi_values = group_df[kpi_name].copy()
    day_index = group_df['day_index'].copy()
    
    # Calculate rolling baseline (expected value)
    rolling_mean, rolling_std = calculate_rolling_baseline(kpi_values, ROLLING_WINDOW_DAYS)
    
    # Calculate trend
    trend = calculate_trend(kpi_values, day_index)
    
    # Calculate seasonality adjustment
    group_df = calculate_seasonality_adjustment(group_df, kpi_name)
    seasonality_factor = group_df['seasonality_factor'].fillna(1.0)
    
    # Expected value: combine rolling mean with trend and seasonality
    # Use rolling mean as base, adjust with trend if available, then apply seasonality
    expected_value = rolling_mean.copy()
    
    # If trend is available and rolling mean is not, use trend
    if trend.notna().any() and rolling_mean.isna().any():
        trend_filled = trend.bfill().ffill()
        expected_value = expected_value.fillna(trend_filled)
    
    # Apply seasonality adjustment
    expected_value = expected_value * seasonality_factor
    
    # Calculate bounds
    # Use rolling std for bounds, with minimum bound width based on percentiles
    rolling_std_filled = rolling_std.fillna(rolling_std.median() if rolling_std.median() > 0 else kpi_values.std())
    
    # Calculate percentile-based bounds as alternative
    rolling_q25 = kpi_values.rolling(window=ROLLING_WINDOW_DAYS, min_periods=MIN_DATA_POINTS).quantile(0.25)
    rolling_q75 = kpi_values.rolling(window=ROLLING_WINDOW_DAYS, min_periods=MIN_DATA_POINTS).quantile(0.75)
    iqr = rolling_q75 - rolling_q25
    
    # Use IQR-based bounds (more robust to outliers) or std-based
    bound_width = np.maximum(
        rolling_std_filled * BOUNDS_STD_MULTIPLIER,
        iqr * 1.5  # 1.5 * IQR is a common outlier detection threshold
    )
    
    # For stockout_rate, ensure bounds are between 0 and 1
    if kpi_name == 'stockout_rate':
        bound_width = bound_width.clip(upper=1.0)
    
    lower_bound = expected_value - bound_width
    upper_bound = expected_value + bound_width
    
    # Clip bounds to reasonable ranges
    if kpi_name == 'stockout_rate':
        lower_bound = lower_bound.clip(lower=0.0, upper=1.0)
        upper_bound = upper_bound.clip(lower=0.0, upper=1.0)
    elif kpi_name == 'gross_margin':
        lower_bound = lower_bound.clip(lower=0.0, upper=1.0)
        upper_bound = upper_bound.clip(lower=0.0, upper=1.0)
    elif kpi_name == 'total_revenue':
        lower_bound = lower_bound.clip(lower=0.0)
    
    return pd.DataFrame({
        'date': group_df['date'],
        'store_id': group_df['store_id'],
        'category': group_df['category'],
        f'{kpi_name}_expected': expected_value,
        f'{kpi_name}_lower_bound': lower_bound,
        f'{kpi_name}_upper_bound': upper_bound
    })

def compute_all_baselines(kpi_df):
    """Compute baselines for all KPIs across all store-category combinations."""
    print("\nComputing baselines...")
    
    # Add time features
    kpi_df = add_time_features(kpi_df)
    
    # KPIs to process
    kpi_names = ['total_revenue', 'gross_margin', 'stockout_rate']
    
    # Process each KPI
    baseline_dfs = []
    
    for kpi_name in kpi_names:
        print(f"  Processing {kpi_name}...")
        
        kpi_baselines = []
        
        # Group by store and category
        for (store_id, category), group in kpi_df.groupby(['store_id', 'category']):
            baseline = compute_baselines_for_group(group, kpi_name)
            kpi_baselines.append(baseline)
        
        # Combine all baselines for this KPI
        kpi_baseline_df = pd.concat(kpi_baselines, ignore_index=True)
        baseline_dfs.append(kpi_baseline_df)
    
    # Merge all KPI baselines
    print("  Merging baselines...")
    merged_baselines = baseline_dfs[0]
    for df in baseline_dfs[1:]:
        merged_baselines = merged_baselines.merge(
            df,
            on=['date', 'store_id', 'category'],
            how='outer'
        )
    
    # Sort by date, store_id, category
    merged_baselines = merged_baselines.sort_values(['date', 'store_id', 'category']).reset_index(drop=True)
    
    # Round numeric columns
    numeric_cols = merged_baselines.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if 'revenue' in col:
            merged_baselines[col] = merged_baselines[col].round(2)
        else:
            merged_baselines[col] = merged_baselines[col].round(4)
    
    print(f"  Generated {len(merged_baselines):,} baseline records")
    
    return merged_baselines

def save_baselines(baselines_df, output_path):
    """Save baselines to CSV."""
    print(f"\nSaving baselines to {output_path}...")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert date back to string for CSV
    baselines_df = baselines_df.copy()
    baselines_df['date'] = pd.to_datetime(baselines_df['date']).dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    baselines_df.to_csv(output_path, index=False)
    print(f"  Saved: {output_path} ({len(baselines_df):,} records)")
    
    # Display summary statistics
    print("\n" + "="*50)
    print("BASELINE SUMMARY STATISTICS")
    print("="*50)
    
    for kpi in ['total_revenue', 'gross_margin', 'stockout_rate']:
        expected_col = f'{kpi}_expected'
        lower_col = f'{kpi}_lower_bound'
        upper_col = f'{kpi}_upper_bound'
        
        if expected_col in baselines_df.columns:
            print(f"\n{kpi}:")
            print(f"  Expected (mean): {baselines_df[expected_col].mean():.4f}")
            print(f"  Lower bound (mean): {baselines_df[lower_col].mean():.4f}")
            print(f"  Upper bound (mean): {baselines_df[upper_col].mean():.4f}")
            print(f"  Bound width (mean): {(baselines_df[upper_col] - baselines_df[lower_col]).mean():.4f}")
    
    print("="*50)

def main():
    """Main function to compute and save baselines."""
    print("="*50)
    print("RETAIL KPI BASELINES")
    print("="*50)
    
    # Load KPI data
    kpi_df = load_kpi_data()
    
    # Compute baselines
    baselines_df = compute_all_baselines(kpi_df)
    
    # Save baselines
    output_path = f"{PROCESSED_DATA_DIR}/{OUTPUT_FILE}"
    save_baselines(baselines_df, output_path)
    
    print("\nBaseline computation complete!")

if __name__ == "__main__":
    main()
