# Retail Operations Anomaly Detection System - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Data Pipeline](#data-pipeline)
4. [Scripts Documentation](#scripts-documentation)
5. [Data Flow](#data-flow)
6. [Running the System](#running-the-system)
7. [Output Files](#output-files)
8. [Common Errors and Solutions](#common-errors-and-solutions)
9. [Dependencies](#dependencies)
10. [Configuration Parameters](#configuration-parameters)

---

## Project Overview

This project implements a comprehensive retail operations anomaly detection system that:
- Generates synthetic retail data for testing
- Processes raw transaction data into daily KPIs
- Learns normal behavior patterns (baselines) for each KPI
- Detects meaningful deviations from baselines
- Analyzes root causes of detected anomalies

The system is designed to help retail operations teams identify and understand operational issues that impact financial performance.

---

## System Architecture

The system follows a modular pipeline architecture:

```
Raw Data → Preprocessing → KPI Calculation → Baseline Learning → Anomaly Detection → Root Cause Analysis
```

### Components:
1. **Data Generation** (`data_generation.py`) - Creates synthetic retail data
2. **Preprocessing** (`preprocessing.py`) - Transforms raw data into daily KPIs
3. **Baseline Learning** (`baselines.py`) - Learns normal behavior patterns
4. **Anomaly Detection** (`detection.py`) - Identifies significant deviations
5. **Root Cause Analysis** (`root_cause.py`) - Explains why anomalies occurred

---

## Data Pipeline

### Input Data Structure

#### Raw Data Files (in `data/raw/`):
- **sales.csv**: Daily sales transactions
  - Columns: `date`, `store_id`, `product_id`, `category`, `units_sold`, `price`, `discount_rate`, `revenue`
- **inventory.csv**: Daily inventory levels
  - Columns: `date`, `store_id`, `product_id`, `stock_on_hand`, `stockout_flag`
- **products.csv**: Product master data
  - Columns: `product_id`, `category`, `supplier_id`, `cost_price`
- **stores.csv**: Store master data
  - Columns: `store_id`, `region`, `store_type`

### Processed Data Files (in `data/processed/`):
- **kpi_daily.csv**: Daily aggregated KPIs by store and category
- **baselines.csv**: Expected values and bounds for each KPI
- **anomalies.csv**: Detected anomaly events
- **root_causes.csv**: Root cause analysis results

---

## Scripts Documentation

### 1. `data_generation.py`

**Purpose**: Generates realistic synthetic retail data for testing and development.

**Key Features**:
- Generates 12 months of daily transaction data
- Creates realistic patterns (weekend boosts, promotions, stockouts)
- Produces 4 CSV files: sales, inventory, products, stores

**Configuration**:
```python
NUM_STORES = 10
NUM_PRODUCTS = 30
NUM_CATEGORIES = 5
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)
```

**Output**: 
- `data/raw/sales.csv`
- `data/raw/inventory.csv`
- `data/raw/products.csv`
- `data/raw/stores.csv`

**Usage**:
```bash
python src/data_generation.py
```

---

### 2. `preprocessing.py`

**Purpose**: Transforms raw retail data into clean daily KPI metrics.

**Key Features**:
- Merges sales, inventory, products, and stores data
- Aggregates to daily level by store and category
- Calculates three KPIs:
  - `total_revenue`: Sum of revenue per day/store/category
  - `gross_margin`: (revenue - cost) / revenue
  - `stockout_rate`: Percentage of products with stockouts

**Processing Steps**:
1. Load all raw CSV files
2. Merge sales with products (to get cost_price)
3. Merge with inventory (to get stockout_flag)
4. Merge with stores (for completeness)
5. Calculate cost: `units_sold * cost_price`
6. Aggregate by date, store_id, category
7. Calculate KPIs
8. Sort by date and save

**Output**: 
- `data/processed/kpi_daily.csv`
  - Columns: `date`, `store_id`, `category`, `total_revenue`, `gross_margin`, `stockout_rate`

**Usage**:
```bash
python src/preprocessing.py
```

**Key Functions**:
- `load_raw_data()`: Loads all raw CSV files
- `merge_data()`: Merges all data sources
- `calculate_kpis()`: Computes daily KPIs
- `save_processed_data()`: Saves results to CSV

---

### 3. `baselines.py`

**Purpose**: Learns normal (healthy) behavior patterns for each KPI.

**Key Features**:
- Uses rolling windows (30 days) to calculate expected values
- Captures trends using linear regression
- Detects seasonality (day-of-week, month-of-year)
- Computes upper and lower bounds for normal behavior

**Baseline Learning Methods**:
1. **Rolling Statistics**: 30-day rolling mean and standard deviation
2. **Trend Detection**: Linear regression on time series
3. **Seasonality Adjustment**: Day-of-week and month-of-year factors
4. **Bounds Calculation**: Uses both standard deviation (2σ) and IQR-based methods

**Configuration**:
```python
ROLLING_WINDOW_DAYS = 30
BOUNDS_STD_MULTIPLIER = 2.0
MIN_DATA_POINTS = 7
```

**Output**: 
- `data/processed/baselines.csv`
  - Columns: `date`, `store_id`, `category`, 
    - `total_revenue_expected`, `total_revenue_lower_bound`, `total_revenue_upper_bound`
    - `gross_margin_expected`, `gross_margin_lower_bound`, `gross_margin_upper_bound`
    - `stockout_rate_expected`, `stockout_rate_lower_bound`, `stockout_rate_upper_bound`

**Usage**:
```bash
python src/baselines.py
```

**Key Functions**:
- `load_kpi_data()`: Loads daily KPI data
- `add_time_features()`: Adds day-of-week, month, etc.
- `calculate_rolling_baseline()`: Computes rolling statistics
- `calculate_trend()`: Fits linear trend
- `calculate_seasonality_adjustment()`: Applies seasonality factors
- `compute_all_baselines()`: Processes all KPIs and entities

**Note**: Early dates may have missing bounds until enough historical data accumulates (typically 30 days).

---

### 4. `detection.py`

**Purpose**: Detects meaningful deviations from learned baselines.

**Key Features**:
- Compares actual KPIs to baseline predictions
- Flags anomalies only if:
  - Values fall outside bounds
  - Deviation persists for multiple consecutive days (≥2 days)
  - Estimated financial impact is significant (≥$100/day)
- Assigns severity levels based on duration and impact

**Detection Logic**:
1. **Out-of-Bounds Detection**: Flags when actual values exceed bounds
2. **Persistence Check**: Requires minimum consecutive days (default: 2)
3. **Financial Impact Calculation**:
   - Revenue impact: difference from expected
   - Margin impact: margin deviation × revenue
   - Stockout impact: estimated lost revenue
4. **Severity Assignment**:
   - Low: 2+ days, $100+ impact
   - Medium: 3+ days, $500+ impact
   - High: 5+ days, $1000+ impact
   - Critical: 7+ days, $5000+ impact

**Configuration**:
```python
MIN_CONSECUTIVE_DAYS = 2
MIN_FINANCIAL_IMPACT = 100.0
```

**Output**: 
- `data/processed/anomalies.csv`
  - Columns: `metric`, `entity`, `store_id`, `category`, `start_date`, `end_date`, 
    `duration_days`, `anomaly_direction`, `avg_impact`, `max_impact`, `severity`

**Usage**:
```bash
python src/detection.py
```

**Key Functions**:
- `load_data()`: Loads KPI and baseline data
- `detect_out_of_bounds()`: Flags out-of-bounds values
- `calculate_financial_impact()`: Computes impact metrics
- `detect_persistent_anomalies()`: Finds consecutive anomaly periods
- `assign_severity()`: Categorizes by severity

---

### 5. `root_cause.py`

**Purpose**: Explains detected operational issues by identifying contributing drivers.

**Key Features**:
- Compares baseline period (30 days before anomaly) vs anomaly period
- Trains RandomForest classifier to distinguish the two periods
- Ranks contributing drivers by importance score
- Shows how each driver changed between periods

**Root Cause Analysis Process**:
1. **Period Definition**: 
   - Baseline: 30 days before anomaly start
   - Anomaly: Duration of detected anomaly
2. **Feature Extraction**:
   - Categorical: supplier_id, store_type, region, category
   - Numerical: discount_rate, stock_on_hand, price, units_sold, cost_price
   - Derived: discount_frequency, low_stock_frequency, avg_markup
3. **Model Training**: RandomForest classifier (50 trees, max_depth=5)
4. **Importance Ranking**: Uses feature importance from trained model
5. **Change Analysis**: Calculates percent change for numerical features

**Configuration**:
```python
BASELINE_PERIOD_DAYS = 30
MIN_SAMPLES_PER_PERIOD = 10
```

**Output**: 
- `data/processed/root_causes.csv`
  - Columns: `anomaly_id`, `store_id`, `category`, `metric`, `severity`, 
    `driver`, `importance_score`, `change`

**Usage**:
```bash
python src/root_cause.py
```

**Key Functions**:
- `prepare_feature_data()`: Merges all raw data sources
- `analyze_anomaly_root_cause()`: Analyzes single anomaly
- `analyze_all_anomalies()`: Processes all anomalies (prioritizes high severity)
- `format_root_causes()`: Formats results for output

**Performance Note**: The script prioritizes critical/high severity anomalies and samples others to avoid timeout on large datasets.

---

## Data Flow

```
┌─────────────────┐
│ data_generation │ → Raw CSVs (sales, inventory, products, stores)
└─────────────────┘
         ↓
┌─────────────────┐
│ preprocessing   │ → kpi_daily.csv (daily KPIs by store/category)
└─────────────────┘
         ↓
┌─────────────────┐
│ baselines       │ → baselines.csv (expected values and bounds)
└─────────────────┘
         ↓
┌─────────────────┐
│ detection       │ → anomalies.csv (detected events)
└─────────────────┘
         ↓
┌─────────────────┐
│ root_cause      │ → root_causes.csv (driver rankings)
└─────────────────┘
```

---

## Running the System

### Complete Pipeline Execution

Run scripts in order:

```bash
# Step 1: Generate data (if needed)
python src/data_generation.py

# Step 2: Preprocess raw data
python src/preprocessing.py

# Step 3: Learn baselines
python src/baselines.py

# Step 4: Detect anomalies
python src/detection.py

# Step 5: Analyze root causes
python src/root_cause.py
```

### Individual Script Execution

Each script can be run independently if previous outputs exist:

```bash
# Just run detection (requires kpi_daily.csv and baselines.csv)
python src/detection.py

# Just run root cause analysis (requires anomalies.csv and raw data)
python src/root_cause.py
```

---

## Output Files

### `data/processed/kpi_daily.csv`
Daily aggregated KPIs:
- **Rows**: One per day/store/category combination
- **Columns**: date, store_id, category, total_revenue, gross_margin, stockout_rate
- **Example**: 18,250 rows (365 days × 10 stores × 5 categories)

### `data/processed/baselines.csv`
Baseline predictions and bounds:
- **Rows**: One per day/store/category combination
- **Columns**: date, store_id, category, plus expected/lower_bound/upper_bound for each KPI
- **Note**: Early dates may have missing bounds until enough history accumulates

### `data/processed/anomalies.csv`
Detected anomaly events:
- **Rows**: One per detected anomaly event
- **Columns**: metric, entity, store_id, category, start_date, end_date, duration_days, 
  anomaly_direction, avg_impact, max_impact, severity
- **Sorted**: By severity (critical → high → medium → low), then by start_date

### `data/processed/root_causes.csv`
Root cause analysis results:
- **Rows**: One per driver per anomaly
- **Columns**: anomaly_id, store_id, category, metric, severity, driver, importance_score, change
- **Sorted**: By anomaly_id, then by importance_score (descending)

---

## Common Errors and Solutions

### 1. **FileNotFoundError: No such file or directory**

**Error Message**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/sales.csv'
```

**Cause**: Missing input files or incorrect directory structure.

**Solution**:
- Ensure `data/raw/` directory exists with required CSV files
- Run `data_generation.py` first to create raw data
- Check file paths in script configuration

---

### 2. **KeyError: Column not found**

**Error Message**:
```
KeyError: 'cost_price'
```

**Cause**: Missing columns in input data or merge failure.

**Solution**:
- Verify all required columns exist in input CSVs
- Check merge operations are successful (use `how='left'` or `how='inner'` appropriately)
- Print column names after loading: `print(df.columns.tolist())`

---

### 3. **FutureWarning: Series.fillna with 'method' is deprecated**

**Error Message**:
```
FutureWarning: Series.fillna with 'method' is deprecated and will raise in a future version.
```

**Cause**: Using deprecated pandas fillna method syntax.

**Solution**:
- Replace `fillna(method='bfill')` with `bfill()`
- Replace `fillna(method='ffill')` with `ffill()`
- **Fixed in**: `baselines.py` line 120

---

### 4. **ValueError: Can only compare identically-labeled Series objects**

**Error Message**:
```
ValueError: Can only compare identically-labeled Series objects
```

**Cause**: Comparing pandas Series with different indices.

**Solution**:
- Reset indices before comparison: `df.reset_index(drop=True)`
- Use `.values` for array comparison
- Ensure Series have same length and alignment

---

### 5. **Timeout / Script takes too long**

**Error Message**:
```
Command timed out
```

**Cause**: Processing too much data, especially in `root_cause.py`.

**Solution**:
- **Implemented**: Script now prioritizes critical/high severity anomalies
- Limits processing to top 20 medium/low severity anomalies
- Consider reducing `BASELINE_PERIOD_DAYS` or `MIN_SAMPLES_PER_PERIOD`
- Process anomalies in batches

---

### 6. **Missing bounds in baselines.csv**

**Symptom**: Empty values in `*_lower_bound` and `*_upper_bound` columns for early dates.

**Cause**: Not enough historical data for rolling window calculation.

**Solution**:
- **Expected behavior**: Bounds require minimum data points (default: 7-15 days)
- Bounds will populate after sufficient history accumulates
- Adjust `MIN_DATA_POINTS` if needed (lower = earlier bounds, less stable)

---

### 7. **Division by zero in gross_margin calculation**

**Error Message**:
```
ZeroDivisionError: division by zero
```

**Cause**: Revenue is zero in some records.

**Solution**:
- **Fixed in**: `preprocessing.py` uses `np.where()` to handle zero revenue
- Formula: `gross_margin = np.where(revenue > 0, (revenue - cost) / revenue, np.nan)`

---

### 8. **Empty anomaly results**

**Symptom**: `anomalies.csv` is empty or has very few records.

**Cause**: Detection thresholds too strict.

**Solution**:
- Lower `MIN_CONSECUTIVE_DAYS` (default: 2)
- Lower `MIN_FINANCIAL_IMPACT` (default: $100)
- Check if baselines are too wide (adjust `BOUNDS_STD_MULTIPLIER`)

---

### 9. **Memory errors with large datasets**

**Error Message**:
```
MemoryError: Unable to allocate array
```

**Cause**: Dataset too large for available memory.

**Solution**:
- Process data in chunks
- Use `dtype` optimization (e.g., `category` dtype for strings)
- Filter data early (by date range, store, etc.)
- Consider using Dask or chunked processing

---

### 10. **LabelEncoder errors in root_cause.py**

**Error Message**:
```
ValueError: y contains previously unseen labels
```

**Cause**: Different categories in baseline vs anomaly period.

**Solution**:
- **Fixed**: Encoders are fit on combined data before encoding
- Ensure all categories are present in combined dataset
- Handle missing categories gracefully

---

### 11. **GroupBy aggregation errors**

**Error Message**:
```
ValueError: No objects to concatenate
```

**Cause**: Empty groups in groupby operations.

**Solution**:
- Check for empty dataframes before groupby
- Add minimum sample checks: `if len(df) < MIN_SAMPLES: return None`
- Handle empty results gracefully

---

### 12. **Date parsing errors**

**Error Message**:
```
ValueError: Unknown datetime string format
```

**Cause**: Date format mismatch in CSV files.

**Solution**:
- Ensure dates are in `YYYY-MM-DD` format
- Use `pd.to_datetime()` with `format='%Y-%m-%d'` if needed
- Check CSV date columns are properly formatted

---

## Dependencies

### Required Python Packages

```python
pandas >= 1.3.0
numpy >= 1.20.0
scikit-learn >= 0.24.0
```

### Installation

```bash
pip install pandas numpy scikit-learn
```

Or using requirements.txt (create if needed):

```txt
pandas>=1.3.0
numpy>=1.20.0
scikit-learn>=0.24.0
```

Then:
```bash
pip install -r requirements.txt
```

---

## Configuration Parameters

### `data_generation.py`
- `NUM_STORES`: Number of stores to generate (default: 10)
- `NUM_PRODUCTS`: Number of products (default: 30)
- `NUM_CATEGORIES`: Number of categories (default: 5)
- `START_DATE`: Start date for data generation
- `END_DATE`: End date for data generation

### `preprocessing.py`
- `RAW_DATA_DIR`: Directory for raw CSV files (default: "data/raw")
- `PROCESSED_DATA_DIR`: Directory for output (default: "data/processed")

### `baselines.py`
- `ROLLING_WINDOW_DAYS`: Days for rolling statistics (default: 30)
- `BOUNDS_STD_MULTIPLIER`: Standard deviations for bounds (default: 2.0)
- `MIN_DATA_POINTS`: Minimum data points before computing baselines (default: 7)

### `detection.py`
- `MIN_CONSECUTIVE_DAYS`: Minimum days of deviation to flag (default: 2)
- `MIN_FINANCIAL_IMPACT`: Minimum daily financial impact to flag (default: $100)
- `SEVERITY_THRESHOLDS`: Dictionary defining severity levels

### `root_cause.py`
- `BASELINE_PERIOD_DAYS`: Days before anomaly to use as baseline (default: 30)
- `MIN_SAMPLES_PER_PERIOD`: Minimum samples needed for analysis (default: 10)

---

## Best Practices

1. **Run scripts in order**: Data generation → Preprocessing → Baselines → Detection → Root Cause
2. **Check outputs**: Verify each step produces expected output before proceeding
3. **Monitor memory**: Large datasets may require chunked processing
4. **Adjust thresholds**: Tune detection parameters based on business requirements
5. **Validate data**: Check for missing values, date ranges, and data quality
6. **Version control**: Track changes to configuration parameters
7. **Error handling**: Add try-except blocks for production use
8. **Logging**: Consider adding logging instead of print statements

---

## Troubleshooting Checklist

- [ ] All required CSV files exist in `data/raw/`
- [ ] Date columns are properly formatted (YYYY-MM-DD)
- [ ] Required columns exist in all input files
- [ ] Python packages are installed (pandas, numpy, scikit-learn)
- [ ] Sufficient disk space for output files
- [ ] Sufficient memory for processing
- [ ] Scripts are run in correct order
- [ ] Configuration parameters are appropriate for dataset size

---

## Future Enhancements

Potential improvements:
1. **Real-time processing**: Stream processing for live data
2. **Database integration**: Store results in database instead of CSV
3. **Visualization**: Dashboard for anomaly visualization
4. **Alerting**: Email/Slack notifications for critical anomalies
5. **Model persistence**: Save trained models for reuse
6. **A/B testing**: Compare different baseline methods
7. **Multi-threading**: Parallel processing for faster execution
8. **API**: REST API for integration with other systems

---

## Contact and Support

For questions or issues:
1. Check this documentation first
2. Review error messages and solutions above
3. Check script comments and docstrings
4. Verify data quality and format
5. Test with smaller datasets first

---

**Last Updated**: January 2026
**Version**: 1.0
