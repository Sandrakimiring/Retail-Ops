import { Box, Grid, TextField, Button } from '@mui/material';
import type { KPIFilters as KPIFiltersType } from '@/types';

interface KPIFiltersProps {
  filters: KPIFiltersType;
  onFiltersChange: (filters: KPIFiltersType) => void;
}

const KPIFilters = ({ filters, onFiltersChange }: KPIFiltersProps) => {
  return (
    <Box sx={{ mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="Start Date"
            type="date"
            value={filters.start_date}
            onChange={(e) => onFiltersChange({ ...filters, start_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <TextField
            fullWidth
            label="End Date"
            type="date"
            value={filters.end_date}
            onChange={(e) => onFiltersChange({ ...filters, end_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
        <Grid item xs={12} sm={4}>
          <Button variant="contained" fullWidth>
            Apply Filters
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default KPIFilters;
