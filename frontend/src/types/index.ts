// Common types for the application

export type Severity = 'critical' | 'high' | 'medium' | 'low';

export type Metric = 'total_revenue' | 'gross_margin' | 'stockout_rate';

export type AnomalyDirection = 'high' | 'low';

export interface Anomaly {
  id: string;
  metric: Metric;
  entity: string;
  store_id: number;
  category: string;
  start_date: string;
  end_date: string;
  duration_days: number;
  anomaly_direction: AnomalyDirection;
  avg_impact: number;
  max_impact: number;
  severity: Severity;
}

export interface AnomalyDetail extends Anomaly {
  kpi_timeseries: KPITimeSeriesPoint[];
  root_causes: RootCause[];
  related_anomalies?: Anomaly[];
}

export interface KPITimeSeriesPoint {
  date: string;
  actual: number;
  expected: number;
  lower_bound: number;
  upper_bound: number;
}

export interface RootCause {
  driver: string;
  importance_score: number;
  change: string;
}

export interface KPIData {
  date: string;
  store_id: number;
  category: string;
  total_revenue: number;
  gross_margin: number;
  stockout_rate: number;
}

export interface Baseline {
  date: string;
  store_id: number;
  category: string;
  total_revenue_expected: number;
  total_revenue_lower_bound: number;
  total_revenue_upper_bound: number;
  gross_margin_expected: number;
  gross_margin_lower_bound: number;
  gross_margin_upper_bound: number;
  stockout_rate_expected: number;
  stockout_rate_lower_bound: number;
  stockout_rate_upper_bound: number;
}

export interface Store {
  store_id: number;
  region: string;
  store_type: string;
}

export interface SummaryStats {
  anomaly_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  total_impact: number;
  avg_impact: number;
  recent_anomalies: Anomaly[];
}

export interface AnomalyFilters {
  page?: number;
  limit?: number;
  severity?: Severity[];
  metric?: Metric[];
  store_id?: number[];
  category?: string[];
  start_date?: string;
  end_date?: string;
  min_impact?: number;
  max_impact?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

export interface KPIFilters {
  start_date: string;
  end_date: string;
  store_id?: number[];
  category?: string[];
  metric?: string[];
}
