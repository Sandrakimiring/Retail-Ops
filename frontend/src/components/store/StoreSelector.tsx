import { Select, MenuItem, FormControl, InputLabel, Box } from '@mui/material';
import type { Store } from '@/types';

interface StoreSelectorProps {
  stores: Store[];
  value: number | null;
  onChange: (id: number) => void;
}

const StoreSelector = ({ stores, value, onChange }: StoreSelectorProps) => {
  return (
    <Box sx={{ mb: 3 }}>
      <FormControl fullWidth sx={{ maxWidth: 400 }}>
        <InputLabel>Select Store</InputLabel>
        <Select
          value={value || ''}
          label="Select Store"
          onChange={(e) => onChange(Number(e.target.value))}
        >
          {stores.map((store) => (
            <MenuItem key={store.store_id} value={store.store_id}>
              Store {store.store_id} - {store.region} - {store.store_type}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default StoreSelector;
