// Placeholder component - to be implemented
import { Paper, Typography, List, ListItem, ListItemText } from '@mui/material'
import type { RootCause } from '@/types'

interface RootCauseDriversProps {
  drivers: RootCause[]
}

const RootCauseDrivers = ({ drivers }: RootCauseDriversProps) => {
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Root Cause Drivers
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Ranked by importance score
      </Typography>
      <List>
        {drivers.length > 0 ? (
          drivers.map((driver, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${index + 1}. ${driver.driver}`}
                secondary={`Importance: ${driver.importance_score.toFixed(4)} • Change: ${driver.change}`}
              />
            </ListItem>
          ))
        ) : (
          <Typography variant="body2" color="text.secondary">
            No root cause data available
          </Typography>
        )}
      </List>
    </Paper>
  )
}

export default RootCauseDrivers
