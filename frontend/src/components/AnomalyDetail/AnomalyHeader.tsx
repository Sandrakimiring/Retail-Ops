// Placeholder component - to be implemented
import { Paper, Typography, Chip, Box } from '@mui/material'
import type { AnomalyDetail } from '@/types'

interface AnomalyHeaderProps {
  anomaly: AnomalyDetail
}

const AnomalyHeader = ({ anomaly }: AnomalyHeaderProps) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" gap={2} alignItems="center" mb={2}>
        <Chip label={anomaly.severity} color="error" size="medium" />
        <Typography variant="h5">{anomaly.metric}</Typography>
      </Box>
      <Typography variant="body2" color="text.secondary">
        Store {anomaly.store_id} • {anomaly.category} • {anomaly.start_date} to {anomaly.end_date}
      </Typography>
    </Paper>
  )
}

export default AnomalyHeader
