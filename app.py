"""
Flask Backend Server for RetailOps Insight Engine
Serves the frontend and provides REST API endpoints for data access.
"""

import os
import json
import csv
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from datetime import datetime

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# Data directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# Cache for loaded data
data_cache = {}

def load_csv(filepath):
    """Load CSV file and return as list of dicts."""
    cache_key = filepath
    if cache_key in data_cache:
        return data_cache[cache_key]
    
    data = []
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric strings to numbers
                parsed_row = {}
                for key, value in row.items():
                    if value == '':
                        parsed_row[key] = None
                    else:
                        try:
                            # Try int first, then float
                            if '.' in value:
                                parsed_row[key] = float(value)
                            else:
                                parsed_row[key] = int(value)
                        except (ValueError, TypeError):
                            parsed_row[key] = value
                data.append(parsed_row)
        data_cache[cache_key] = data
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    
    return data

def clear_cache():
    """Clear the data cache."""
    global data_cache
    data_cache = {}

# ===== Static File Routes =====

@app.route('/')
def serve_index():
    """Serve the main frontend application."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(app.static_folder, path)

# ===== API Routes =====

@app.route('/api/health')
def api_health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/summary')
def api_summary():
    """Get dashboard summary data."""
    kpi_daily = load_csv(os.path.join(PROCESSED_DATA_DIR, 'kpi_daily.csv'))
    anomalies = load_csv(os.path.join(PROCESSED_DATA_DIR, 'anomalies.csv'))
    
    if not kpi_daily:
        return jsonify({'error': 'No data available'}), 404
    
    # Get latest date
    dates = sorted(set(row['date'] for row in kpi_daily))
    latest_date = dates[-1] if dates else None
    
    # Filter to latest date
    latest_data = [row for row in kpi_daily if row['date'] == latest_date]
    
    # Calculate totals
    total_revenue = sum(row.get('total_revenue', 0) or 0 for row in latest_data)
    margins = [row.get('gross_margin', 0) or 0 for row in latest_data]
    avg_margin = sum(margins) / len(margins) if margins else 0
    
    # Count anomalies by severity
    severity_counts = {
        'critical': sum(1 for a in anomalies if a.get('severity') == 'critical'),
        'high': sum(1 for a in anomalies if a.get('severity') == 'high'),
        'medium': sum(1 for a in anomalies if a.get('severity') == 'medium'),
        'low': sum(1 for a in anomalies if a.get('severity') == 'low')
    }
    
    # Calculate health score
    total_anomalies = len(anomalies)
    weighted_impact = (
        severity_counts['critical'] * 10 +
        severity_counts['high'] * 5 +
        severity_counts['medium'] * 2 +
        severity_counts['low'] * 1
    )
    health_score = max(0, min(100, 100 - weighted_impact))
    
    return jsonify({
        'latestDate': latest_date,
        'totalRevenue': total_revenue,
        'avgMargin': avg_margin,
        'totalAnomalies': total_anomalies,
        'severityCounts': severity_counts,
        'healthScore': health_score
    })

@app.route('/api/anomalies')
def api_anomalies():
    """Get anomalies with optional filters."""
    anomalies = load_csv(os.path.join(PROCESSED_DATA_DIR, 'anomalies.csv'))
    root_causes = load_csv(os.path.join(PROCESSED_DATA_DIR, 'root_causes.csv'))
    
    # Get filter parameters
    severity = request.args.get('severity', 'all')
    metric = request.args.get('metric', 'all')
    store = request.args.get('store', 'all')
    
    # Apply filters
    filtered = anomalies
    if severity != 'all':
        filtered = [a for a in filtered if a.get('severity') == severity]
    if metric != 'all':
        filtered = [a for a in filtered if a.get('metric') == metric]
    if store != 'all':
        filtered = [a for a in filtered if str(a.get('store_id')) == str(store)]
    
    # Enrich with root causes
    result = []
    for anomaly in filtered:
        start_date = anomaly.get('start_date', '').replace('-', '')
        anomaly_id = f"{anomaly.get('store_id')}_{anomaly.get('category')}_{start_date}"
        
        drivers = [rc for rc in root_causes if rc.get('anomaly_id') == anomaly_id]
        drivers = sorted(drivers, key=lambda x: x.get('importance_score', 0), reverse=True)[:5]
        
        result.append({
            **anomaly,
            'anomalyId': anomaly_id,
            'drivers': drivers
        })
    
    return jsonify(result)

@app.route('/api/anomalies/<anomaly_id>')
def api_anomaly_detail(anomaly_id):
    """Get detailed information for a specific anomaly."""
    anomalies = load_csv(os.path.join(PROCESSED_DATA_DIR, 'anomalies.csv'))
    root_causes = load_csv(os.path.join(PROCESSED_DATA_DIR, 'root_causes.csv'))
    
    # Find the anomaly
    anomaly = None
    for a in anomalies:
        start_date = a.get('start_date', '').replace('-', '')
        aid = f"{a.get('store_id')}_{a.get('category')}_{start_date}"
        if aid == anomaly_id:
            anomaly = a
            break
    
    if not anomaly:
        return jsonify({'error': 'Anomaly not found'}), 404
    
    # Get all drivers
    drivers = [rc for rc in root_causes if rc.get('anomaly_id') == anomaly_id]
    drivers = sorted(drivers, key=lambda x: x.get('importance_score', 0), reverse=True)
    
    return jsonify({
        **anomaly,
        'anomalyId': anomaly_id,
        'drivers': drivers
    })

@app.route('/api/trends')
def api_trends():
    """Get time series data for trends."""
    kpi_daily = load_csv(os.path.join(PROCESSED_DATA_DIR, 'kpi_daily.csv'))
    baselines = load_csv(os.path.join(PROCESSED_DATA_DIR, 'baselines.csv'))
    
    # Get filter parameters
    store = request.args.get('store', 'all')
    category = request.args.get('category', 'all')
    metric = request.args.get('metric', 'total_revenue')
    
    # Filter data
    data = kpi_daily
    if store != 'all':
        data = [d for d in data if str(d.get('store_id')) == str(store)]
    if category != 'all':
        data = [d for d in data if d.get('category') == category]
    
    # Group by date and aggregate
    date_groups = {}
    for row in data:
        date = row.get('date')
        if date not in date_groups:
            date_groups[date] = []
        date_groups[date].append(row.get(metric, 0) or 0)
    
    # Build time series
    expected_col = f'{metric}_expected'
    time_series = []
    
    for date in sorted(date_groups.keys()):
        actual_values = date_groups[date]
        actual = sum(actual_values) / len(actual_values) if actual_values else 0
        
        # Get baseline expected value
        baseline_rows = [b for b in baselines if b.get('date') == date]
        if store != 'all':
            baseline_rows = [b for b in baseline_rows if str(b.get('store_id')) == str(store)]
        if category != 'all':
            baseline_rows = [b for b in baseline_rows if b.get('category') == category]
        
        expected = None
        if baseline_rows:
            expected_values = [b.get(expected_col, 0) or 0 for b in baseline_rows]
            expected = sum(expected_values) / len(expected_values) if expected_values else None
        
        time_series.append({
            'date': date,
            'actual': actual,
            'expected': expected
        })
    
    return jsonify(time_series)

@app.route('/api/entities')
def api_entities():
    """Get list of stores and categories."""
    stores = load_csv(os.path.join(RAW_DATA_DIR, 'stores.csv'))
    kpi_daily = load_csv(os.path.join(PROCESSED_DATA_DIR, 'kpi_daily.csv'))
    
    categories = sorted(set(row.get('category') for row in kpi_daily if row.get('category')))
    
    return jsonify({
        'stores': stores,
        'categories': categories
    })

@app.route('/api/entities/<entity_type>/<entity_id>')
def api_entity_detail(entity_type, entity_id):
    """Get details for a specific entity."""
    kpi_daily = load_csv(os.path.join(PROCESSED_DATA_DIR, 'kpi_daily.csv'))
    anomalies = load_csv(os.path.join(PROCESSED_DATA_DIR, 'anomalies.csv'))
    stores = load_csv(os.path.join(RAW_DATA_DIR, 'stores.csv'))
    
    # Filter data
    if entity_type == 'store':
        entity_data = [d for d in kpi_daily if str(d.get('store_id')) == str(entity_id)]
        entity_anomalies = [a for a in anomalies if str(a.get('store_id')) == str(entity_id)]
        metadata = next((s for s in stores if str(s.get('store_id')) == str(entity_id)), {})
        metadata['name'] = f"Store {entity_id}"
    else:
        entity_data = [d for d in kpi_daily if d.get('category') == entity_id]
        entity_anomalies = [a for a in anomalies if a.get('category') == entity_id]
        metadata = {'name': entity_id, 'type': 'category'}
    
    # Calculate health metrics
    def calculate_health(data, metric):
        values = [d.get(metric, 0) or 0 for d in data]
        if not values:
            return 50
        mean = sum(values) / len(values)
        if mean == 0:
            return 50
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean if mean != 0 else 0
        return max(0, min(100, int(100 - cv * 100)))
    
    return jsonify({
        'metadata': metadata,
        'revenueHealth': calculate_health(entity_data, 'total_revenue'),
        'marginHealth': calculate_health(entity_data, 'gross_margin'),
        'stockoutHealth': 100 - calculate_health(entity_data, 'stockout_rate'),
        'activeAnomalies': entity_anomalies,
        'dataPoints': len(entity_data)
    })

@app.route('/api/heatmap')
def api_heatmap():
    """Get heatmap data."""
    kpi_daily = load_csv(os.path.join(PROCESSED_DATA_DIR, 'kpi_daily.csv'))
    anomalies = load_csv(os.path.join(PROCESSED_DATA_DIR, 'anomalies.csv'))
    
    stores = sorted(set(d.get('store_id') for d in kpi_daily if d.get('store_id')))
    categories = sorted(set(d.get('category') for d in kpi_daily if d.get('category')))
    
    heatmap = []
    for store_id in stores:
        cells = []
        for category in categories:
            store_anomalies = [
                a for a in anomalies 
                if a.get('store_id') == store_id and a.get('category') == category
            ]
            
            status = 'healthy'
            if any(a.get('severity') in ['critical', 'high'] for a in store_anomalies):
                status = 'danger'
            elif any(a.get('severity') == 'medium' for a in store_anomalies):
                status = 'warning'
            
            cells.append({
                'category': category,
                'status': status,
                'count': len(store_anomalies)
            })
        
        heatmap.append({
            'storeId': store_id,
            'cells': cells
        })
    
    return jsonify({
        'stores': stores,
        'categories': categories,
        'heatmap': heatmap
    })

@app.route('/api/config', methods=['GET', 'PUT'])
def api_config():
    """Get or update configuration."""
    config_path = os.path.join(BASE_DIR, 'config.json')
    
    default_config = {
        'minConsecutiveDays': 2,
        'minFinancialImpact': 100,
        'baselineWindow': 30,
        'boundsMultiplier': 2.0,
        'severityThresholds': {
            'low': {'days': 2, 'impact': 100},
            'medium': {'days': 3, 'impact': 500},
            'high': {'days': 5, 'impact': 1000},
            'critical': {'days': 7, 'impact': 5000}
        }
    }
    
    if request.method == 'GET':
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = default_config
        return jsonify(config)
    
    else:  # PUT
        config = request.get_json()
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return jsonify({'status': 'saved', 'config': config})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/pipeline/run', methods=['POST'])
def api_run_pipeline():
    """Trigger a pipeline re-run."""
    import subprocess
    
    try:
        scripts = [
            'src/data_generation.py',
            'src/preprocessing.py',
            'src/baselines.py',
            'src/detection.py',
            'src/root_cause.py'
        ]
        
        for script in scripts:
            script_path = os.path.join(BASE_DIR, script)
            if os.path.exists(script_path):
                subprocess.run(['python', script_path], check=True, cwd=BASE_DIR)
        
        # Clear cache after pipeline run
        clear_cache()
        
        return jsonify({
            'status': 'success',
            'message': 'Pipeline completed successfully',
            'timestamp': datetime.now().isoformat()
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'status': 'error',
            'message': f'Pipeline failed: {e}'
        }), 500

# ===== Error Handlers =====

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ===== Main =====

if __name__ == '__main__':
    print("Starting RetailOps Insight Engine...")
    print(f"Data directory: {DATA_DIR}")
    print(f"Frontend directory: {app.static_folder}")
    print("\nServer running at http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
