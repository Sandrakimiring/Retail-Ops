// Utility functions

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(d);
}

export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    critical: '#F44336',
    high: '#FF9800',
    medium: '#FBC02D',
    low: '#2196F3',
  };
  return colors[severity] || '#666';
}
