import { useState } from 'react'
import { Box, Typography } from '@mui/material'
import KPISummaryCards from '@/components/KPIDashboard/KPISummaryCards';
import RevenueChart from '@/components/KPIDashboard/RevenueChart';
import MarginChart from '@/components/KPIDashboard/MarginChart';
import StockoutChart from '@/components/KPIDashboard/StockoutChart';
import KPIFilters from '@/components/KPIDashboard/KPIFilters';
import type { KPIFilters as KPIFiltersType } from '@/types'

const KPIDashboard = () => {
  const [filters, setFilters] = useState<KPIFiltersType>({
    start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        KPI Performance Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Monitor KPIs across stores and categories with baseline visualization
      </Typography>

      <KPIFilters filters={filters} onFiltersChange={setFilters} />

      <Box sx={{ mt: 3 }}>
        <KPISummaryCards filters={filters} />
      </Box>

      <Box sx={{ mt: 3 }}>
        <RevenueChart filters={filters} />
      </Box>

      <Box sx={{ mt: 3 }}>
        <MarginChart filters={filters} />
      </Box>

      <Box sx={{ mt: 3 }}>
        <StockoutChart filters={filters} />
      </Box>
    </Box>
  )
}

export default KPIDashboard
