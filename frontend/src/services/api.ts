import axios from 'axios';
import type {
  Anomaly,
  AnomalyDetail,
  AnomalyFilters,
  PaginatedResponse,
  KPIData,
  Baseline,
  Store,
  SummaryStats,
  RootCause,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Anomalies API
export const anomaliesApi = {
  getAll: async (filters?: AnomalyFilters): Promise<PaginatedResponse<Anomaly>> => {
    const response = await apiClient.get('/anomalies', { params: filters });
    return response.data;
  },

  getById: async (id: string): Promise<AnomalyDetail> => {
    const response = await apiClient.get(`/anomalies/${id}`);
    return response.data;
  },
};

// KPIs API
export const kpisApi = {
  list: async (params: {
    start_date: string;
    end_date: string;
    store_id?: number[];
    category?: string[];
    metric?: string[];
  }): Promise<{ data: KPIData[]; summary: any }> => {
    const response = await apiClient.get('/kpis', { params });
    return response.data;
  },
};

// Baselines API
export const baselinesApi = {
  list: async (params: {
    start_date: string;
    end_date: string;
    store_id?: number;
    category?: string;
    metric?: string;
  }): Promise<{ data: Baseline[] }> => {
    const response = await apiClient.get('/baselines', { params });
    return response.data;
  },
};

// Root Causes API
export const rootCausesApi = {
  getByAnomalyId: async (anomalyId: string): Promise<{ anomaly_id: string; drivers: RootCause[] }> => {
    const response = await apiClient.get(`/root-causes/${anomalyId}`);
    return response.data;
  },
};

// Stores API
export const storesApi = {
  list: async (): Promise<{ data: Store[] }> => {
    const response = await apiClient.get('/stores');
    return response.data;
  },

  getPerformance: async (
    storeId: number,
    params?: { start_date?: string; end_date?: string }
  ): Promise<any> => {
    const response = await apiClient.get(`/stores/${storeId}/performance`, { params });
    return response.data;
  },
};

// Summary API
export const summaryApi = {
  get: async (params?: { start_date?: string; end_date?: string }): Promise<SummaryStats> => {
    const response = await apiClient.get('/summary', { params });
    return response.data;
  },
};
