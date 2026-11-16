import { Grid, Card, CardContent, Box, Typography, Skeleton } from '@mui/material'
import { SummaryStats } from '@/types'

interface SummaryCardsProps {
  data?: SummaryStats
  loading: boolean
}

const SummaryCards = ({ data, loading }: SummaryCardsProps) => {
  const cards = [
    {
      label: 'Critical',
      value: data?.anomaly_counts.critical || 0,
      color: '#F44336',
      icon: '🚨',
    },
    {
      label: 'High',
      value: data?.anomaly_counts.high || 0,
      color: '#FF9800',
      icon: '⚠️',
    },
    {
      label: 'Medium',
      value: data?.anomaly_counts.medium || 0,
      color: '#FBC02D',
      icon: '📊',
    },
    {
      label: 'Low',
      value: data?.anomaly_counts.low || 0,
      color: '#2196F3',
      icon: 'ℹ️',
    },
  ]

  return (
    <Grid container spacing={3}>
      {cards.map((card) => (
        <Grid item xs={12} sm={6} md={3} key={card.label}>
          <Card
            sx={{
              borderLeft: `4px solid ${card.color}`,
              height: '100%',
            }}
          >
            <CardContent>
              {loading ? (
                <Skeleton variant="rectangular" height={80} />
              ) : (
                <Box display="flex" alignItems="center" gap={2}>
                  <Typography variant="h3" component="div">
                    {card.icon}
                  </Typography>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {card.label}
                    </Typography>
                    <Typography variant="h4" component="div" fontWeight="bold">
                      {card.value}
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  )
}

export default SummaryCards
