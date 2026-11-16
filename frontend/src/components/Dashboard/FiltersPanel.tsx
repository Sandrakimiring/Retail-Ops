// Placeholder component - to be implemented
import { Box, Paper, Typography } from '@mui/material'
import type { AnomalyFilters } from '@/types'

interface FiltersPanelProps {
  filters: AnomalyFilters
  onFiltersChange: (filters: AnomalyFilters) => void
}

const FiltersPanel = ({ filters, onFiltersChange }: FiltersPanelProps) => {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Filters
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Filter panel implementation coming soon...
      </Typography>
    </Paper>
  )
}

export default FiltersPanel
