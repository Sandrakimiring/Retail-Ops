import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { kpisApi } from '@/services/api';

interface CategoryPerformanceProps {
  storeId: number;
}

const CategoryPerformance = ({ storeId }: CategoryPerformanceProps) => {
  const { data, isLoading } = useQuery({
    queryKey: ['categoryPerformance', storeId],
    queryFn: () =>
      kpisApi.list({
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        store_id: [storeId],
      }),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  // Group by category
  const categoryData = data?.data.reduce((acc, kpi) => {
    if (!acc[kpi.category]) {
      acc[kpi.category] = { revenue: 0, margin: 0, stockout: 0, count: 0 };
    }
    acc[kpi.category].revenue += kpi.total_revenue;
    acc[kpi.category].margin += kpi.gross_margin;
    acc[kpi.category].stockout += kpi.stockout_rate;
    acc[kpi.category].count += 1;
    return acc;
  }, {} as Record<string, { revenue: number; margin: number; stockout: number; count: number }>);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Performance by Category
        </Typography>
        {categoryData && Object.keys(categoryData).length > 0 ? (
          <Box>
            {Object.entries(categoryData).map(([category, stats]) => (
              <Box key={category} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {category}
                </Typography>
                <Box display="flex" gap={3} mt={1}>
                  <Typography variant="body2">
                    Revenue: ${(stats.revenue / stats.count).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </Typography>
                  <Typography variant="body2">
                    Margin: {((stats.margin / stats.count) * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2">
                    Stockout: {((stats.stockout / stats.count) * 100).toFixed(1)}%
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No category data available
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default CategoryPerformance;
