import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Box, Typography, Grid } from '@mui/material'
import { anomaliesApi, summaryApi } from '@/services/api'
import SummaryCards from '@/components/Dashboard/SummaryCards'
import AnomaliesTable from '@/components/Dashboard/AnomaliesTable'
import AnomaliesTimeline from '@/components/Dashboard/AnomaliesTimeline'
import ImpactCard from '@/components/Dashboard/ImpactCard'
import FiltersPanel from '@/components/Dashboard/FiltersPanel'
import type { AnomalyFilters } from '@/types'

const Dashboard = () => {
  const [filters, setFilters] = useState<AnomalyFilters>({
    page: 1,
    limit: 50,
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: () => summaryApi.get(),
  })

  const { data: anomalies, isLoading: anomaliesLoading } = useQuery({
    queryKey: ['anomalies', filters],
    queryFn: () => anomaliesApi.getAll(filters),
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Anomaly Overview Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Central hub for monitoring all detected anomalies
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <SummaryCards data={summary} loading={summaryLoading} />
        </Grid>

        <Grid item xs={12}>
          <ImpactCard data={summary} loading={summaryLoading} />
        </Grid>

        <Grid item xs={12}>
          <FiltersPanel filters={filters} onFiltersChange={setFilters} />
        </Grid>

        <Grid item xs={12}>
          <AnomaliesTimeline data={anomalies?.data} loading={anomaliesLoading} />
        </Grid>

        <Grid item xs={12}>
          <AnomaliesTable
            data={anomalies?.data}
            pagination={anomalies?.pagination}
            loading={anomaliesLoading}
            onPageChange={(page) => setFilters({ ...filters, page })}
          />
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
