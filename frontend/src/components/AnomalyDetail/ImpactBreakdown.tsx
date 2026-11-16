// Placeholder component - to be implemented
import { Paper, Typography, Grid, Box } from '@mui/material'
import type { AnomalyDetail } from '@/types'

interface ImpactBreakdownProps {
  anomaly: AnomalyDetail
}

const ImpactBreakdown = ({ anomaly }: ImpactBreakdownProps) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Financial Impact Breakdown
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Revenue Impact
            </Typography>
            <Typography variant="h6" color="error">
              -${(anomaly.max_impact * 0.6).toFixed(2)}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={12} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Margin Impact
            </Typography>
            <Typography variant="h6" color="error">
              -${(anomaly.max_impact * 0.3).toFixed(2)}
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={12} md={4}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Stockout Impact
            </Typography>
            <Typography variant="h6" color="error">
              -${(anomaly.max_impact * 0.1).toFixed(2)}
            </Typography>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  )
}

export default ImpactBreakdown
