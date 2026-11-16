import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, Typography, Box, Grid, Chip, CircularProgress } from '@mui/material';
import { storesApi } from '@/services/api';

interface StoreInfoProps {
  storeId: number;
}

const StoreInfo = ({ storeId }: StoreInfoProps) => {
  const { data: performance, isLoading } = useQuery({
    queryKey: ['storePerformance', storeId],
    queryFn: () => storesApi.getPerformance(storeId),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  if (!performance) {
    return <Typography>Store information not available</Typography>;
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5">Store {storeId}</Typography>
          <Box>
            <Chip label={performance.region || 'Unknown'} color="primary" sx={{ mr: 1 }} />
            <Chip label={performance.store_type || 'Unknown'} color="secondary" />
          </Box>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Total Revenue
            </Typography>
            <Typography variant="h6">${(performance.total_revenue || 0).toLocaleString()}</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Gross Margin
            </Typography>
            <Typography variant="h6">{((performance.gross_margin || 0) * 100).toFixed(1)}%</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Stockout Rate
            </Typography>
            <Typography variant="h6">{((performance.stockout_rate || 0) * 100).toFixed(1)}%</Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              Anomalies
            </Typography>
            <Typography variant="h6">{performance.anomaly_count || 0}</Typography>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default StoreInfo;
