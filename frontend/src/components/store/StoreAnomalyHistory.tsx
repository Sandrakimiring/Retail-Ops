import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { anomaliesApi } from '@/services/api';

interface StoreAnomalyHistoryProps {
  storeId: number;
}

const StoreAnomalyHistory = ({ storeId }: StoreAnomalyHistoryProps) => {
  const { data, isLoading } = useQuery({
    queryKey: ['storeAnomalies', storeId],
    queryFn: () => anomaliesApi.getAll({ store_id: [storeId], limit: 10 }),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Anomalies
        </Typography>
        {data?.data && data.data.length > 0 ? (
          <Box>
            {data.data.map((anomaly) => (
              <Box key={anomaly.id} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  {anomaly.metric} - {anomaly.category}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {anomaly.start_date} to {anomaly.end_date} ({anomaly.duration_days} days)
                </Typography>
              </Box>
            ))}
          </Box>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No anomalies found for this store
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default StoreAnomalyHistory;
