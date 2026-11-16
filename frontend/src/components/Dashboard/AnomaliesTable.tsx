import { useNavigate } from 'react-router-dom'
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
  Pagination,
  Skeleton,
} from '@mui/material'
import { Anomaly, Severity } from '@/types'

interface AnomaliesTableProps {
  data?: Anomaly[]
  pagination?: {
    page: number
    limit: number
    total: number
    total_pages: number
  }
  loading: boolean
  onPageChange: (page: number) => void
}

const getSeverityColor = (severity: Severity) => {
  const colors = {
    critical: 'error',
    high: 'warning',
    medium: 'info',
    low: 'default',
  } as const
  return colors[severity]
}

const AnomaliesTable = ({ data, pagination, loading, onPageChange }: AnomaliesTableProps) => {
  const navigate = useNavigate()

  if (loading) {
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {[...Array(9)].map((_, i) => (
                <TableCell key={i}>
                  <Skeleton />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {[...Array(5)].map((_, i) => (
              <TableRow key={i}>
                {[...Array(9)].map((_, j) => (
                  <TableCell key={j}>
                    <Skeleton />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  return (
    <Paper>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Severity</TableCell>
              <TableCell>Metric</TableCell>
              <TableCell>Store</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Start Date</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Direction</TableCell>
              <TableCell>Max Impact</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.map((anomaly) => (
              <TableRow
                key={anomaly.id}
                hover
                sx={{ cursor: 'pointer' }}
                onClick={() => navigate(`/anomalies/${anomaly.id}`)}
              >
                <TableCell>
                  <Chip
                    label={anomaly.severity}
                    color={getSeverityColor(anomaly.severity)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{anomaly.metric}</TableCell>
                <TableCell>Store {anomaly.store_id}</TableCell>
                <TableCell>{anomaly.category}</TableCell>
                <TableCell>{anomaly.start_date}</TableCell>
                <TableCell>{anomaly.duration_days} days</TableCell>
                <TableCell>
                  <Chip
                    label={anomaly.anomaly_direction === 'high' ? '↑ High' : '↓ Low'}
                    size="small"
                    color={anomaly.anomaly_direction === 'high' ? 'success' : 'error'}
                  />
                </TableCell>
                <TableCell>${anomaly.max_impact.toFixed(2)}</TableCell>
                <TableCell>
                  <Box
                    component="span"
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(`/anomalies/${anomaly.id}`)
                    }}
                    sx={{ color: 'primary.main', cursor: 'pointer', textDecoration: 'underline' }}
                  >
                    View Details
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {pagination && pagination.total_pages > 1 && (
        <Box display="flex" justifyContent="center" p={2}>
          <Pagination
            count={pagination.total_pages}
            page={pagination.page}
            onChange={(_, page) => onPageChange(page)}
            color="primary"
          />
        </Box>
      )}
    </Paper>
  )
}

export default AnomaliesTable
