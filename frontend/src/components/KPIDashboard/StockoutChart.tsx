import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { kpisApi } from '@/services/api';
import type { KPIFilters } from '@/types';

interface StockoutChartProps {
  filters: KPIFilters;
}

const StockoutChart = ({ filters }: StockoutChartProps) => {
  const { data, isLoading } = useQuery({
    queryKey: ['kpis', 'stockout', filters],
    queryFn: () => kpisApi.list({ ...filters, metric: ['stockout_rate'] }),
  });

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" p={3}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Stockout Rate
        </Typography>
        <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Chart will be implemented with Recharts
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default StockoutChart;
