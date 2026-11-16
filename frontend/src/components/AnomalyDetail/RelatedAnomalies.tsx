// Placeholder component - to be implemented
import { Paper, Typography } from '@mui/material'

interface RelatedAnomaliesProps {
  storeId: number
  category: string
  currentAnomalyId?: string
}

const RelatedAnomalies = ({ storeId, category, currentAnomalyId }: RelatedAnomaliesProps) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Related Anomalies
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Related anomalies table implementation coming soon...
      </Typography>
    </Paper>
  )
}

export default RelatedAnomalies
