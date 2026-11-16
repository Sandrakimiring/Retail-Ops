// Placeholder component - to be implemented
import { Paper, Typography } from '@mui/material'
import type { Anomaly } from '@/types'

interface AnomaliesTimelineProps {
  data?: Anomaly[]
  loading: boolean
}

const AnomaliesTimeline = ({ data, loading }: AnomaliesTimelineProps) => {
  return (
    <Paper sx={{ p: 3, minHeight: 300 }}>
      <Typography variant="h6" gutterBottom>
        Recent Anomalies Timeline
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Timeline chart implementation coming soon...
      </Typography>
    </Paper>
  )
}

export default AnomaliesTimeline
