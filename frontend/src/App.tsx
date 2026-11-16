import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import AnomalyDetail from './pages/AnomalyDetail/AnomalyDetail';
import KPIDashboard from './pages/KPIDashboard/KPIDashboard';
import StorePerformance from './pages/StorePerformance/StorePerformance';
import { Box, Typography } from '@mui/material';

// Placeholder pages
const RootCauseAnalysis = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      Root Cause Analysis Explorer
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Interactive exploration of root cause drivers - Coming soon...
    </Typography>
  </Box>
);

const Settings = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      Settings
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Configure baseline parameters and detection thresholds - Coming soon...
    </Typography>
  </Box>
);

const NotFound = () => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '60vh',
      textAlign: 'center',
    }}
  >
    <Typography variant="h1" component="h1" sx={{ fontSize: '6rem', fontWeight: 'bold' }}>
      404
    </Typography>
    <Typography variant="h5" component="h2" gutterBottom>
      Page Not Found
    </Typography>
    <Typography variant="body1" color="text.secondary">
      The page you are looking for does not exist.
    </Typography>
  </Box>
);

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/anomalies/:id" element={<AnomalyDetail />} />
        <Route path="/kpi" element={<KPIDashboard />} />
        <Route path="/stores" element={<StorePerformance />} />
        <Route path="/root-causes" element={<RootCauseAnalysis />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Layout>
  );
}

export default App;
