# Retail Operations Frontend

Frontend application for the Retail Operations Anomaly Detection System, built with React, TypeScript, and Material-UI.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library
- **React Router** - Routing
- **React Query (TanStack Query)** - Data fetching and caching
- **Recharts** - Charting library
- **Axios** - HTTP client

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main layout wrapper
│   │   ├── Header.tsx       # App header
│   │   ├── Sidebar.tsx      # Navigation sidebar
│   │   ├── dashboard/       # Dashboard-specific components
│   │   ├── anomaly/         # Anomaly detail components
│   │   ├── kpi/             # KPI dashboard components
│   │   └── store/           # Store performance components
│   ├── pages/               # Page components
│   │   ├── DashboardPage.tsx
│   │   ├── AnomalyDetailPage.tsx
│   │   ├── KPIPerformancePage.tsx
│   │   ├── StorePerformancePage.tsx
│   │   ├── RootCauseAnalysisPage.tsx
│   │   └── SettingsPage.tsx
│   ├── services/            # API service layer
│   │   └── api.ts           # API client and endpoints
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/               # Utility functions
│   │   └── index.ts
│   ├── hooks/               # Custom React hooks (to be added)
│   ├── context/             # React context providers (to be added)
│   ├── theme.ts             # MUI theme configuration
│   ├── App.tsx              # Main app component with routes
│   ├── main.tsx             # App entry point
│   └── index.css             # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

```bash
cd frontend
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:

```bash
npm run build
```

The production build will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors
- `npm run format` - Format code with Prettier
- `npm run type-check` - Type check without emitting

## Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENV=development
```

See `.env.example` for reference.

## API Integration

The frontend expects a backend API running on `http://localhost:8000` (configurable via environment variables).

API endpoints are defined in `src/services/api.ts`:

- `/api/anomalies` - List and get anomalies
- `/api/kpis` - Get KPI data
- `/api/baselines` - Get baseline data
- `/api/root-causes/{id}` - Get root cause analysis
- `/api/stores` - Get stores list and performance
- `/api/summary` - Get summary statistics

## Development Workflow

1. **Component Development**: Create components in `src/components/`
2. **Page Development**: Create pages in `src/pages/`
3. **API Integration**: Add API calls in `src/services/api.ts`
4. **Type Definitions**: Add types in `src/types/index.ts`
5. **Styling**: Use Material-UI components and theme

## Component Status

### ✅ Implemented
- Project structure
- Routing setup
- Layout components (Header, Sidebar)
- Page components (skeleton)
- API service layer
- Type definitions
- Theme configuration

### 🚧 To Be Implemented
- Dashboard components (SummaryCards, ImpactCard, AnomaliesTable, etc.)
- Anomaly detail components (TimeSeriesChart, RootCauseDrivers, etc.)
- KPI dashboard components (Charts, Filters)
- Store performance components
- Root cause analysis explorer
- Settings page

## Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Configured with TypeScript and React rules
- **Prettier**: Code formatting
- **Naming**: PascalCase for components, camelCase for functions/variables

## Path Aliases

The project uses path aliases for cleaner imports:

```typescript
import { Anomaly } from '@/types';
import { anomaliesApi } from '@/services/api';
import { formatCurrency } from '@/utils';
```

## Next Steps

1. Implement dashboard components based on mockups
2. Add chart components using Recharts
3. Implement filtering and pagination
4. Add loading states and error handling
5. Connect to backend API
6. Add unit tests
7. Add E2E tests

## Contributing

1. Create a feature branch
2. Make your changes
3. Run linting and type checking
4. Submit a pull request

---

**Version**: 1.0.0  
**Last Updated**: January 2026
