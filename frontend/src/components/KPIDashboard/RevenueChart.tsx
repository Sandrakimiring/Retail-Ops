import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { kpisApi } from '@/services/api';
import type { KPIFilters } from '@/types';

interface RevenueChartProps {
  filters: KPIFilters;
}

const RevenueChart = ({ filters }: RevenueChartProps) => {
  const { data, isLoading } = useQuery({
    queryKey: ['kpis', 'revenue', filters],
    queryFn: () => kpisApi.list({ ...filters, metric: ['total_revenue'] }),
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
          Total Revenue
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

export default RevenueChart;
