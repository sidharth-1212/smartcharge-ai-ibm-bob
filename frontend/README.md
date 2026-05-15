# SmartCharge AI Frontend

React-based dashboard for the SmartCharge AI EV Charging Optimizer.

## Features

- **Real-time Telemetry Display**: Live power gauges for solar, grid, and battery
- **Bob's Decision Engine**: View AI-powered charging decisions and reasoning
- **Historical Charts**: Visualize telemetry data over time
- **Analytics Dashboard**: Track cost savings and renewable energy usage
- **Manual Controls**: Override Bob's decisions when needed
- **Event Log**: See recent charging decisions and their reasoning

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server
npm run dev
```

The application will be available at http://localhost:3000

## Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Configuration

Environment variables can be configured in `.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_POLL_INTERVAL=5000
```

## Components

- **Dashboard**: Main container component
- **PowerGauge**: Circular gauge for power metrics
- **BobController**: Display and control Bob's decisions
- **EventLog**: Scrolling log of recent decisions
- **TelemetryCharts**: Line charts for historical data
- **Analytics**: Cost savings and insights

## API Integration

The frontend polls the backend API every 5 seconds for:
- Latest telemetry data
- Bob's latest decision
- Historical data for charts

## Technology Stack

- React 18
- Vite
- Tailwind CSS
- Recharts
- Axios

## Troubleshooting

If you see connection errors:
1. Ensure the backend is running on http://localhost:8000
2. Check that CORS is enabled in the backend
3. Verify the API endpoints are accessible

## License

MIT