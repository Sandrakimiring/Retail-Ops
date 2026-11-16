// Placeholder component - to be implemented with Recharts
import { Paper, Typography } from '@mui/material'
import type { KPITimeSeries } from '@/types'

interface TimeSeriesChartProps {
  data?: KPITimeSeries[]
}

const TimeSeriesChart = ({ data }: TimeSeriesChartProps) => {
  return (
    <Paper sx={{ p: 3, minHeight: 400 }}>
      <Typography variant="h6" gutterBottom>
        KPI Time Series
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Time series chart implementation with Recharts coming soon...
      </Typography>
    </Paper>
  )
}

export default TimeSeriesChart
