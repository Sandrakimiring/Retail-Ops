"""
Anomaly Detection Script for Retail Operations
Detects meaningful deviations from learned baselines.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configuration
PROCESSED_DATA_DIR = "data/processed"
KPI_FILE = "kpi_daily.csv"
BASELINES_FILE = "baselines.csv"
OUTPUT_FILE = "anomalies.csv"

# Detection parameters
MIN_CONSECUTIVE_DAYS = 2  # Minimum days of deviation to flag
MIN_FINANCIAL_IMPACT = 100.0  # Minimum daily financial impact in dollars to flag
SEVERITY_THRESHOLDS = {
    'low': {'days': 2, 'impact': 100},
    'medium': {'days': 3, 'impact': 500},
    'high': {'days': 5, 'impact': 1000},
    'critical': {'days': 7, 'impact': 5000}
}

def load_data():
    """Load KPI data and baselines."""
    print("Loading data...")
    
    kpi_df = pd.read_csv(f"{PROCESSED_DATA_DIR}/{KPI_FILE}")
    kpi_df['date'] = pd.to_datetime(kpi_df['date'])
    
    baselines_df = pd.read_csv(f"{PROCESSED_DATA_DIR}/{BASELINES_FILE}")
    baselines_df['date'] = pd.to_datetime(baselines_df['date'])
    
    print(f"  Loaded {len(kpi_df):,} KPI records")
    print(f"  Loaded {len(baselines_df):,} baseline records")
    
    return kpi_df, baselines_df

def merge_kpi_with_baselines(kpi_df, baselines_df):
    """Merge KPI data with baselines."""
    print("\nMerging KPI data with baselines...")
    
    merged_df = kpi_df.merge(
        baselines_df,
        on=['date', 'store_id', 'category'],
        how='inner'
    )
    
    print(f"  Merged dataset: {len(merged_df):,} records")
    
    return merged_df

def detect_out_of_bounds(merged_df):
    """Detect when actual values fall outside bounds."""
    print("\nDetecting out-of-bounds values...")
    
    # Initialize anomaly flags
    merged_df['revenue_anomaly'] = False
    merged_df['margin_anomaly'] = False
    merged_df['stockout_anomaly'] = False
    
    # Check revenue anomalies (both high and low)
    revenue_mask = (
        (merged_df['total_revenue'] < merged_df['total_revenue_lower_bound']) |
        (merged_df['total_revenue'] > merged_df['total_revenue_upper_bound'])
    ) & merged_df['total_revenue_lower_bound'].notna()
    merged_df.loc[revenue_mask, 'revenue_anomaly'] = True
    
    # Check margin anomalies (both high and low)
    margin_mask = (
        (merged_df['gross_margin'] < merged_df['gross_margin_lower_bound']) |
        (merged_df['gross_margin'] > merged_df['gross_margin_upper_bound'])
    ) & merged_df['gross_margin_lower_bound'].notna()
    merged_df.loc[margin_mask, 'margin_anomaly'] = True
    
    # Check stockout anomalies (only high - low stockout is good)
    stockout_mask = (
        merged_df['stockout_rate'] > merged_df['stockout_rate_upper_bound']
    ) & merged_df['stockout_rate_upper_bound'].notna()
    merged_df.loc[stockout_mask, 'stockout_anomaly'] = True
    
    print(f"  Revenue anomalies: {revenue_mask.sum():,}")
    print(f"  Margin anomalies: {margin_mask.sum():,}")
    print(f"  Stockout anomalies: {stockout_mask.sum():,}")
    
    return merged_df

def calculate_financial_impact(merged_df):
    """Calculate estimated financial impact of deviations."""
    print("\nCalculating financial impact...")
    
    # Revenue impact: difference between actual and expected
    merged_df['revenue_impact'] = merged_df['total_revenue'] - merged_df['total_revenue_expected']
    
    # Margin impact: difference in margin * revenue
    # Negative margin deviation means lower profit
    margin_deviation = merged_df['gross_margin'] - merged_df['gross_margin_expected']
    merged_df['margin_impact'] = margin_deviation * merged_df['total_revenue']
    
    # Stockout impact: estimated lost revenue
    # Assume stockout rate above expected means lost sales
    stockout_deviation = merged_df['stockout_rate'] - merged_df['stockout_rate_expected']
    # Estimate: each 1% stockout above expected = ~1% lost revenue
    merged_df['stockout_impact'] = stockout_deviation * merged_df['total_revenue'] * 0.01
    
    # Total financial impact (absolute value)
    merged_df['total_impact'] = (
        merged_df['revenue_impact'].abs() + 
        merged_df['margin_impact'].abs() + 
        merged_df['stockout_impact'].abs()
    )
    
    print(f"  Average daily revenue impact: ${merged_df['revenue_impact'].abs().mean():.2f}")
    print(f"  Average daily margin impact: ${merged_df['margin_impact'].abs().mean():.2f}")
    print(f"  Average daily stockout impact: ${merged_df['stockout_impact'].abs().mean():.2f}")
    
    return merged_df

def detect_persistent_anomalies(merged_df, metric_col, anomaly_col):
    """Detect consecutive days of anomalies for a specific metric."""
    # Sort by entity and date
    merged_df = merged_df.sort_values(['store_id', 'category', 'date']).reset_index(drop=True)
    
    # Group by store and category
    anomalies = []
    
    for (store_id, category), group in merged_df.groupby(['store_id', 'category']):
        group = group.sort_values('date').reset_index(drop=True)
        
        # Find consecutive anomaly periods
        in_anomaly = False
        anomaly_start = None
        anomaly_indices = []
        
        for idx, row in group.iterrows():
            if row[anomaly_col] and pd.notna(row[f'{metric_col}_lower_bound']):
                if not in_anomaly:
                    # Start of new anomaly period
                    in_anomaly = True
                    anomaly_start = row['date']
                    anomaly_indices = [idx]
                else:
                    # Continuation of anomaly
                    anomaly_indices.append(idx)
            else:
                if in_anomaly:
                    # End of anomaly period
                    if len(anomaly_indices) >= MIN_CONSECUTIVE_DAYS:
                        # Get the rows for this anomaly period
                        anomaly_rows = group.loc[anomaly_indices]
                        
                        # Calculate aggregate metrics
                        impacts = anomaly_rows['total_impact'].dropna()
                        if len(impacts) > 0:
                            avg_impact = impacts.mean()
                            max_impact = impacts.max()
                        else:
                            avg_impact = 0
                            max_impact = 0
                        
                        # Use max impact for significance check
                        if max_impact >= MIN_FINANCIAL_IMPACT or metric_col == 'stockout_rate':
                            first_row = anomaly_rows.iloc[0]
                            last_row = anomaly_rows.iloc[-1]
                            anomalies.append({
                                'metric': metric_col,
                                'store_id': store_id,
                                'category': category,
                                'start_date': anomaly_start,
                                'end_date': last_row['date'],
                                'duration_days': len(anomaly_indices),
                                'avg_impact': avg_impact,
                                'max_impact': max_impact,
                                'anomaly_direction': 'high' if first_row[metric_col] > first_row[f'{metric_col}_expected'] else 'low'
                            })
                    in_anomaly = False
                    anomaly_indices = []
        
        # Handle case where anomaly continues to end of dataset
        if in_anomaly and len(anomaly_indices) >= MIN_CONSECUTIVE_DAYS:
            anomaly_rows = group.loc[anomaly_indices]
            impacts = anomaly_rows['total_impact'].dropna()
            if len(impacts) > 0:
                avg_impact = impacts.mean()
                max_impact = impacts.max()
            else:
                avg_impact = 0
                max_impact = 0
            
            if max_impact >= MIN_FINANCIAL_IMPACT or metric_col == 'stockout_rate':
                first_row = anomaly_rows.iloc[0]
                last_row = anomaly_rows.iloc[-1]
                anomalies.append({
                    'metric': metric_col,
                    'store_id': store_id,
                    'category': category,
                    'start_date': anomaly_start,
                    'end_date': last_row['date'],
                    'duration_days': len(anomaly_indices),
                    'avg_impact': avg_impact,
                    'max_impact': max_impact,
                    'anomaly_direction': 'high' if first_row[metric_col] > first_row[f'{metric_col}_expected'] else 'low'
                })
    
    return pd.DataFrame(anomalies)

def assign_severity(anomalies_df):
    """Assign severity levels based on duration and impact."""
    def get_severity(row):
        days = row['duration_days']
        impact = row['max_impact']
        
        # Check thresholds in order of severity
        if days >= SEVERITY_THRESHOLDS['critical']['days'] and impact >= SEVERITY_THRESHOLDS['critical']['impact']:
            return 'critical'
        elif days >= SEVERITY_THRESHOLDS['high']['days'] and impact >= SEVERITY_THRESHOLDS['high']['impact']:
            return 'high'
        elif days >= SEVERITY_THRESHOLDS['medium']['days'] and impact >= SEVERITY_THRESHOLDS['medium']['impact']:
            return 'medium'
        elif days >= SEVERITY_THRESHOLDS['low']['days'] and impact >= SEVERITY_THRESHOLDS['low']['impact']:
            return 'low'
        else:
            return 'low'  # Default to low if thresholds not met
    
    anomalies_df['severity'] = anomalies_df.apply(get_severity, axis=1)
    return anomalies_df

def format_entity(store_id, category):
    """Format entity identifier."""
    return f"Store_{store_id}_{category}"

def detect_all_anomalies(merged_df):
    """Detect anomalies for all metrics."""
    print("\nDetecting persistent anomalies...")
    
    all_anomalies = []
    
    # Detect revenue anomalies
    print("  Processing revenue anomalies...")
    revenue_anomalies = detect_persistent_anomalies(
        merged_df[merged_df['revenue_anomaly']].copy(),
        'total_revenue',
        'revenue_anomaly'
    )
    if len(revenue_anomalies) > 0:
        all_anomalies.append(revenue_anomalies)
        print(f"    Found {len(revenue_anomalies)} revenue anomaly events")
    
    # Detect margin anomalies
    print("  Processing margin anomalies...")
    margin_anomalies = detect_persistent_anomalies(
        merged_df[merged_df['margin_anomaly']].copy(),
        'gross_margin',
        'margin_anomaly'
    )
    if len(margin_anomalies) > 0:
        all_anomalies.append(margin_anomalies)
        print(f"    Found {len(margin_anomalies)} margin anomaly events")
    
    # Detect stockout anomalies
    print("  Processing stockout anomalies...")
    stockout_anomalies = detect_persistent_anomalies(
        merged_df[merged_df['stockout_anomaly']].copy(),
        'stockout_rate',
        'stockout_anomaly'
    )
    if len(stockout_anomalies) > 0:
        all_anomalies.append(stockout_anomalies)
        print(f"    Found {len(stockout_anomalies)} stockout anomaly events")
    
    # Combine all anomalies
    if all_anomalies:
        combined_anomalies = pd.concat(all_anomalies, ignore_index=True)
        
        # Assign severity
        combined_anomalies = assign_severity(combined_anomalies)
        
        # Format entity
        combined_anomalies['entity'] = combined_anomalies.apply(
            lambda row: format_entity(row['store_id'], row['category']),
            axis=1
        )
        
        # Select and reorder columns
        output_cols = ['metric', 'entity', 'store_id', 'category', 'start_date', 
                      'end_date', 'duration_days', 'anomaly_direction', 
                      'avg_impact', 'max_impact', 'severity']
        combined_anomalies = combined_anomalies[output_cols]
        
        # Sort by severity and start_date
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        combined_anomalies['severity_order'] = combined_anomalies['severity'].map(severity_order)
        combined_anomalies = combined_anomalies.sort_values(
            ['severity_order', 'start_date', 'max_impact'],
            ascending=[False, True, False]
        ).drop(columns=['severity_order'])
        
        print(f"\n  Total anomaly events detected: {len(combined_anomalies)}")
        
        return combined_anomalies
    else:
        return pd.DataFrame(columns=['metric', 'entity', 'store_id', 'category', 'start_date', 
                                    'end_date', 'duration_days', 'anomaly_direction', 
                                    'avg_impact', 'max_impact', 'severity'])

def save_anomalies(anomalies_df, output_path):
    """Save detected anomalies to CSV."""
    print(f"\nSaving anomalies to {output_path}...")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert dates to strings
    anomalies_df = anomalies_df.copy()
    anomalies_df['start_date'] = pd.to_datetime(anomalies_df['start_date']).dt.strftime('%Y-%m-%d')
    anomalies_df['end_date'] = pd.to_datetime(anomalies_df['end_date']).dt.strftime('%Y-%m-%d')
    
    # Round numeric columns
    anomalies_df['avg_impact'] = anomalies_df['avg_impact'].round(2)
    anomalies_df['max_impact'] = anomalies_df['max_impact'].round(2)
    
    # Save to CSV
    anomalies_df.to_csv(output_path, index=False)
    print(f"  Saved: {output_path} ({len(anomalies_df)} records)")
    
    # Display summary statistics
    print("\n" + "="*50)
    print("ANOMALY DETECTION SUMMARY")
    print("="*50)
    
    if len(anomalies_df) > 0:
        print(f"\nTotal events detected: {len(anomalies_df)}")
        print(f"\nBy severity:")
        severity_counts = anomalies_df['severity'].value_counts()
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in severity_counts:
                print(f"  {severity.capitalize()}: {severity_counts[severity]}")
        
        print(f"\nBy metric:")
        metric_counts = anomalies_df['metric'].value_counts()
        for metric, count in metric_counts.items():
            print(f"  {metric}: {count}")
        
        print(f"\nTop 5 events by impact:")
        top_events = anomalies_df.head(5)
        for idx, row in top_events.iterrows():
            print(f"  {row['entity']} - {row['metric']} ({row['severity']}): "
                  f"${row['max_impact']:.2f} impact over {row['duration_days']} days")
    else:
        print("\nNo significant anomalies detected!")
    
    print("="*50)

def main():
    """Main function to detect anomalies."""
    print("="*50)
    print("RETAIL ANOMALY DETECTION")
    print("="*50)
    
    # Load data
    kpi_df, baselines_df = load_data()
    
    # Merge data
    merged_df = merge_kpi_with_baselines(kpi_df, baselines_df)
    
    # Detect out-of-bounds values
    merged_df = detect_out_of_bounds(merged_df)
    
    # Calculate financial impact
    merged_df = calculate_financial_impact(merged_df)
    
    # Detect persistent anomalies
    anomalies_df = detect_all_anomalies(merged_df)
    
    # Save anomalies
    output_path = f"{PROCESSED_DATA_DIR}/{OUTPUT_FILE}"
    save_anomalies(anomalies_df, output_path)
    
    print("\nAnomaly detection complete!")

if __name__ == "__main__":
    main()
