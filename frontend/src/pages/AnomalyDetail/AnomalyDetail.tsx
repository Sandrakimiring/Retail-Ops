import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Box, Typography, CircularProgress, Alert } from '@mui/material'
import { anomaliesApi, rootCausesApi } from '@/services/api'
import AnomalyHeader from '@/components/AnomalyDetail/AnomalyHeader'
import TimeSeriesChart from '@/components/AnomalyDetail/TimeSeriesChart'
import ImpactBreakdown from '@/components/AnomalyDetail/ImpactBreakdown'
import RootCauseDrivers from '@/components/AnomalyDetail/RootCauseDrivers'
import RelatedAnomalies from '@/components/AnomalyDetail/RelatedAnomalies'

const AnomalyDetail = () => {
  const { id } = useParams<{ id: string }>()

  const { data: anomaly, isLoading, error } = useQuery({
    queryKey: ['anomaly', id],
    queryFn: () => anomaliesApi.getById(id!),
    enabled: !!id,
  })

  const { data: rootCauses } = useQuery({
    queryKey: ['rootCauses', id],
    queryFn: () => rootCausesApi.getByAnomalyId(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error || !anomaly) {
    return (
      <Alert severity="error">
        Failed to load anomaly details. Please try again later.
      </Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Anomaly Details
      </Typography>

      <AnomalyHeader anomaly={anomaly} />

      <Box sx={{ mt: 3 }}>
        <TimeSeriesChart data={anomaly.kpi_timeseries} />
      </Box>

      <Box sx={{ mt: 3 }}>
        <ImpactBreakdown anomaly={anomaly} />
      </Box>

      <Box sx={{ mt: 3 }}>
        <RootCauseDrivers drivers={rootCauses?.drivers || []} />
      </Box>

      <Box sx={{ mt: 3 }}>
        <RelatedAnomalies
          storeId={anomaly.store_id}
          category={anomaly.category}
          currentAnomalyId={id}
        />
      </Box>
    </Box>
  )
}

export default AnomalyDetail
