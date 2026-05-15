# SmartCharge AI - Telemetry Simulator

This microservice generates realistic EV charging telemetry data and sends it to the backend API every 5 seconds.

## Features

- **Realistic Solar Generation**: Simulates solar power generation with time-of-day variations (0-5.5 kW)
- **Dynamic Grid Pricing**: Models electricity pricing with peak hours ($0.12-0.35/kWh)
- **EV Battery Simulation**: Tracks battery state of charge (0-100%) with realistic charging rates
- **Time-of-Day Simulation**: Complete 24-hour cycle simulation
  - Morning (6-10am): Solar ramping up
  - Midday (10am-4pm): Peak solar generation
  - Evening (4-10pm): Solar declining, peak grid pricing
  - Night (10pm-6am): No solar, low grid pricing
- **HTTP API Integration**: Sends telemetry to backend via POST requests

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to set BACKEND_URL if needed
   ```

3. **Run the simulator**:
   ```bash
   python simulator.py
   ```

### Docker

Run with Docker:
```bash
docker build -t smartcharge-simulator .
docker run --rm smartcharge-simulator
```

### Docker Compose

The simulator is included in the main docker-compose.yml:
```bash
docker-compose up simulator
```

## Configuration

Environment variables (optional):

- `BACKEND_URL`: Backend API URL (default: `http://backend:8000`)

## Telemetry Data Format

The simulator generates JSON telemetry with the following structure:

```json
{
  "timestamp": "2026-05-15T16:00:00.000Z",
  "iteration": 1,
  "time_of_day_factor": 0.5,
  "simulated_hour": 12.0,
  "solar": {
    "generation_kw": 5.2,
    "max_capacity_kw": 5.5,
    "utilization_percent": 94.5
  },
  "grid": {
    "price_per_kwh": 0.15,
    "draw_kw": 0.0,
    "status": "NORMAL"
  },
  "ev_battery": {
    "soc_percent": 45.5,
    "capacity_kwh": 75.0,
    "charging_rate_kw": 11.0,
    "estimated_time_to_full_hours": 3.72
  },
  "charging": {
    "mode": "FAST_CHARGE",
    "power_source": "SOLAR",
    "cost_per_hour": 0.0
  },
  "metadata": {
    "simulator_version": "1.0.0",
    "location": "San Francisco, CA",
    "timezone": "America/Los_Angeles"
  }
}
```

## API Endpoint

The simulator sends telemetry to:
```
POST http://backend:8000/api/telemetry/ingest
Content-Type: application/json
```

## Charging Modes

The simulator uses simple logic to determine charging mode:

- **FAST_CHARGE**: When solar > 4.0 kW and battery < 80%
- **ECO_MODE**: When solar > 2.0 kW, grid price < $0.20/kWh, and battery < 90%
- **PAUSED**: All other conditions

In production, charging decisions would be made by the IBM watsonx.ai Bob agent based on optimization algorithms.

## Simulation Parameters

- **Battery Capacity**: 75 kWh (Tesla Model 3 Long Range)
- **Solar Max**: 5.5 kW
- **Fast Charging Rate**: 11 kW (Level 2 charger)
- **Eco Charging Rate**: 3.5 kW
- **Simulation Cycle**: 24 hours compressed into 288 seconds (5 minutes)
- **Update Interval**: 5 seconds

## Troubleshooting

### Backend Connection Issues

If the simulator cannot connect to the backend:
- Check that the backend service is running
- Verify the `BACKEND_URL` environment variable
- Check Docker network connectivity (if using Docker)

The simulator will continue running in offline mode if the backend is unavailable, logging warnings but not stopping execution.

### Testing Without Backend

To test the simulator without a backend:
```bash
python simulator.py
```

The simulator will print telemetry to console and log connection warnings, but will continue generating data.

## Development

The simulator is designed to be:
- **Standalone**: Can run independently for testing
- **Resilient**: Continues operation if backend is unavailable
- **Realistic**: Uses mathematical models for solar and pricing
- **Extensible**: Easy to add new telemetry fields or modify behavior

## License

Part of the SmartCharge AI project. See main LICENSE file.