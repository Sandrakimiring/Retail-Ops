// Placeholder component - to be implemented
import { Card, CardContent, Typography } from '@mui/material'
import type { SummaryStats } from '@/types'

interface ImpactCardProps {
  data?: SummaryStats
  loading: boolean
}

const ImpactCard = ({ data, loading }: ImpactCardProps) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Total Financial Impact
        </Typography>
        {loading ? (
          <Typography>Loading...</Typography>
        ) : (
          <Typography variant="h4" color="primary">
            ${data?.total_impact.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'}
          </Typography>
        )}
      </CardContent>
    </Card>
  )
}

export default ImpactCard
