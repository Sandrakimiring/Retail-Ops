// Placeholder component - to be implemented
import { Grid, Card, CardContent, Typography } from '@mui/material'
import type { KPIFilters } from '@/types'

interface KPISummaryCardsProps {
  filters: KPIFilters
}

const KPISummaryCards = ({ filters }: KPISummaryCardsProps) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6">Total Revenue</Typography>
            <Typography variant="h4" color="primary">
              $0.00
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6">Gross Margin</Typography>
            <Typography variant="h4" color="primary">
              0%
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6">Stockout Rate</Typography>
            <Typography variant="h4" color="primary">
              0%
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )
}

export default KPISummaryCards
