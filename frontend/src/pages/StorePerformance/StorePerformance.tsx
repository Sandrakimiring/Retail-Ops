import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Box, Typography, CircularProgress } from '@mui/material'
import { storesApi } from '@/services/api'
import StoreSelector from '@/components/store/StoreSelector'
import StoreInfo from '@/components/store/StoreInfo'
import StoreAnomalyHistory from '@/components/store/StoreAnomalyHistory'
import CategoryPerformance from '@/components/store/CategoryPerformance'

const StorePerformance = () => {
  const { storeId } = useParams<{ storeId?: string }>()
  const [selectedStoreId, setSelectedStoreId] = useState<number | null>(
    storeId ? parseInt(storeId) : null
  )

  const { data: stores } = useQuery({
    queryKey: ['stores'],
    queryFn: () => storesApi.list(),
  })

  const { data: storePerformance, isLoading } = useQuery({
    queryKey: ['storePerformance', selectedStoreId],
    queryFn: () => storesApi.getPerformance(selectedStoreId!),
    enabled: !!selectedStoreId,
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Store Performance
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Store-level operational health and performance metrics
      </Typography>

      <StoreSelector
        stores={stores?.data || []}
        value={selectedStoreId || 1}
        onChange={(id) => setSelectedStoreId(id)}
      />

      {isLoading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      ) : storePerformance ? (
        <>
          <Box sx={{ mt: 3 }}>
            <StoreInfo storeId={selectedStoreId!} />
          </Box>

          <Box sx={{ mt: 3 }}>
            <StoreAnomalyHistory storeId={selectedStoreId!} />
          </Box>

          <Box sx={{ mt: 3 }}>
            <CategoryPerformance storeId={selectedStoreId!} />
          </Box>
        </>
      ) : (
        <Typography variant="body1" color="text.secondary" sx={{ mt: 3 }}>
          Please select a store to view performance metrics
        </Typography>
      )}
    </Box>
  )
}

export default StorePerformance
