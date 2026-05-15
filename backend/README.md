# SmartCharge AI Backend

FastAPI backend with IBM watsonx.ai Bob integration for intelligent EV charging optimization.

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── alembic/               # Database migrations
│   ├── versions/          # Migration scripts
│   ├── env.py            # Migration environment
│   └── script.py.mako    # Migration template
├── app/
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── database.py       # Database & Redis connections
│   ├── models.py         # SQLAlchemy ORM models
│   ├── routers/          # API endpoints
│   │   ├── telemetry.py  # Telemetry ingestion & history
│   │   ├── bob.py        # IBM Bob decision endpoints
│   │   └── charging.py   # Charging control endpoints
│   ├── services/         # Business logic
│   │   ├── bob_service.py          # IBM Bob API integration
│   │   ├── decision_engine.py      # Decision orchestration
│   │   └── telemetry_processor.py  # Telemetry processing
│   └── utils/            # Utility functions
└── tests/                # Test suite
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- IBM watsonx.ai Bob API key

### Installation

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Set up database:**
```bash
# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head
```

4. **Start the server:**
```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

5. **Access API documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## 📡 API Endpoints

### Health & Info
- `GET /health` - Health check with service status
- `GET /` - API information and endpoints

### Telemetry
- `POST /api/telemetry/ingest` - Ingest telemetry data (auto-triggers Bob decision)
- `GET /api/telemetry/latest` - Get most recent telemetry
- `GET /api/telemetry/history` - Get telemetry history (paginated)
- `GET /api/telemetry/{id}` - Get specific telemetry by ID
- `DELETE /api/telemetry/{id}` - Delete telemetry record

### Bob Decisions
- `POST /api/bob/decision` - Request charging decision from IBM Bob
- `GET /api/bob/decisions/latest` - Get most recent decision
- `GET /api/bob/decisions/history` - Get decision history (paginated)
- `GET /api/bob/decisions/{id}` - Get specific decision by ID
- `POST /api/bob/decisions/{id}/apply` - Mark decision as applied
- `POST /api/bob/decisions/{id}/override` - Override decision with reason

### Charging Control
- `POST /api/charging/mode` - Set charging mode manually
- `GET /api/charging/status` - Get current charging status
- `GET /api/charging/modes` - Get available charging modes
- `POST /api/charging/pause` - Pause charging (convenience)
- `POST /api/charging/resume` - Resume charging (convenience)
- `POST /api/charging/fast-charge` - Enable fast charging (convenience)

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# IBM Bob API
IBM_BOB_API_KEY=your_api_key_here
IBM_BOB_API_URL=https://api.watsonx.ai/v1/bob
IBM_BOB_MODEL_ID=ibm/granite-13b-chat-v2

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/smartcharge_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development
```

See `.env.example` for all available options.

## 🗄️ Database Models

### Telemetry
Stores real-time data from the EV charging system:
- Solar generation (kW)
- Grid price ($/kWh)
- Battery state of charge (%)
- Charging power (kW)
- Weather conditions

### Decision
Stores AI-generated charging decisions from IBM Bob:
- Charging mode (FAST_CHARGE, ECO_MODE, PAUSED)
- Reasoning and confidence score
- Cost and time estimates
- Renewable energy percentage

### User
User accounts and preferences (optional for MVP):
- Preferred charging modes
- Cost limits
- Notification settings

### ChargingSession
Analytics for charging sessions:
- Energy delivered
- Cost tracking
- Renewable energy usage

## 🔄 Decision Flow

1. **Telemetry Ingestion** → Simulator sends telemetry to `/api/telemetry/ingest`
2. **Validation** → TelemetryProcessor validates and stores data
3. **Decision Request** → DecisionEngine formats data for Bob
4. **Bob API Call** → BobService calls IBM watsonx.ai Bob
5. **Response Parsing** → Extract decision, reasoning, and confidence
6. **Storage** → Store decision in database
7. **Return** → Send decision back to simulator/frontend

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_telemetry.py

# Run with verbose output
pytest -v
```

## 🔍 Monitoring

### Logs
Logs are written to:
- Console (stdout)
- File: `logs/smartcharge.log` (if configured)

### Health Check
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "timestamp": "2026-05-15T16:17:00.000Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "bob_api": "configured"
  }
}
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql postgresql://smartcharge:password@localhost:5432/smartcharge_db
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

### IBM Bob API Issues
```bash
# Test Bob API connection
python test_bob_api.py
```

See `README_BOB_SETUP.md` for detailed Bob configuration.

## 📚 Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t smartcharge-backend .

# Run container
docker run -p 8000:8000 --env-file .env smartcharge-backend
```

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS
- [ ] Configure logging to external service
- [ ] Set up monitoring (Sentry, Datadog)
- [ ] Use production database with backups
- [ ] Configure rate limiting
- [ ] Set up load balancing

## 📖 API Documentation

Full API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

See `CONTRIBUTING.md` in the root directory.

## 📄 License

See `LICENSE` in the root directory.

---

**Made with Bob** 🤖 - Powered by IBM watsonx.ai