# FastAPI CQRS Observability

> Production-ready FastAPI backend with CQRS pattern, idempotency, and full observability stack

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- ⚡ **FastAPI** - Modern, fast web framework
- 🔄 **CQRS Pattern** - Separate read/write models
- 🔐 **Idempotency** - Prevent duplicate operations
- 📊 **Full Observability** - Prometheus + Jaeger + Structured Logs
- 🐘 **PostgreSQL** - Reliable data persistence
- 🐳 **Docker Ready** - Complete containerization
- ✅ **High Performance** - P95 latency < 100ms

## 🚀 Quick Start

### Prerrequisitos

- Python 3.13
- Docker y Docker Compose
- Make

### Using Docker (Recommended)

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd fastapi-cqrs-observability
cp .env.sample .env

# 2. Start all services
docker-compose up -d

# 3. Verify health
curl http://localhost:8000/health
```

### Using Make

```bash
make docker-up    # Start services
make test         # Run tests
make docker-down  # Stop services
```

**🌐 Services**:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Jaeger UI: http://localhost:16686
- Prometheus: http://localhost:9090


## 📖 API Usage

### Create User

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "name": "Ana",
    "email": "ana@example.com",
    "password": "S3guro!123",
    "display_name": "Ana G"
  }'
```

**Respuesta (201)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Ana",
  "email": "ana@example.com",
  "display_name": "Ana G",
  "created_at": "2025-10-05T12:00:00Z"
}
```

### Get User

```bash
curl http://localhost:8000/users/{user_id}
```

### Health Checks

```bash
# Liveness probe - checks if app is running
curl http://localhost:8000/health

# Readiness probe - checks if app is ready (DB, resources)
curl http://localhost:8000/ready
```

**Health Response**:
```json
{
  "status": "healthy",
  "service": "signup-service",
  "timestamp": "2025-11-04T16:00:00",
  "uptime_seconds": 3600.5
}
```

**Ready Response**:
```json
{
  "status": "ready",
  "service": "signup-service",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection is active"
    },
    "system": {
      "cpu": {"usage_percent": 15.2, "count": 8},
      "memory": {"total_mb": 16384, "available_mb": 8192, "used_percent": 50.0},
      "disk": {"total_gb": 500, "free_gb": 250, "used_percent": 50.0}
    }
  }
}
```

### Interactive Documentation

Open http://localhost:8000/docs in your browser for full API documentation.

---

## 🧪 Testing

### Setup

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (includes locust, code quality tools)
pip install -r requirements-dev.txt
```

### Unit Tests

```bash
make test
# or
pytest tests/ -v --cov=app --cov-report=html
```

### Load Testing

```bash
# Install dev dependencies first (includes locust)
pip install -r requirements-dev.txt

# Run load test
locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 10 --run-time 2m
```

**Performance SLOs**:
- ✅ P95 latency < 100ms
- ✅ Error rate < 1%
- ✅ Zero duplicates

---

## 🏗️ Arquitectura

### Patrón CQRS

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│      FastAPI Application        │
│  ┌───────────────────────────┐  │
│  │ RequestContext Middleware │  │
│  └───────────┬───────────────┘  │
│  ┌───────────▼───────────────┐  │
│  │ Idempotency Middleware    │  │
│  └───────────┬───────────────┘  │
│  ┌───────────▼───────────────┐  │
│  │    UserService (CQRS)     │  │
│  └───────────┬───────────────┘  │
└──────────────┼──────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ Write Model │ │ Read Model  │
│   (users)   │ │(users_read) │
└─────────────┘ └─────────────┘
```

### Componentes Clave

1. **Middleware de Idempotencia**: Cachea respuestas por `Idempotency-Key` (24h TTL)
2. **CQRS**: Separación de write-model (normalizado) y read-model (denormalizado)
3. **Observabilidad**: Logs estructurados + Prometheus + Jaeger
4. **Validaciones**: Pydantic schemas + DB constraints

---

## 📊 Observability

### Logs

```bash
docker-compose logs -f app
```

### Metrics (Prometheus)

Access metrics at http://localhost:8000/metrics

**Key Metrics**:
- `http_request_duration_seconds` - Request latency
- `signup_requests_total` - Signup operations
- `signup_duplicates_total` - Duplicate attempts
- `idempotency_hits_total` - Cache hits

### Traces (Jaeger)

1. Open http://localhost:16686
2. Select service: `signup-service`
3. View distributed traces

---

## 🛠️ Development

### Local Setup (without Docker)

```bash
# 1. Crear virtualenv
python3.13 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar PostgreSQL (Docker)
docker-compose up -d postgres

# 4. Configurar .env
cp .env.sample .env
# Editar DB_DSN si es necesario

# 5. Ejecutar migraciones
python -m aerich init -t app.core.database.TORTOISE_ORM
python -m aerich init-db
python -m aerich migrate
python -m aerich upgrade

# 6. Iniciar aplicación
python -m uvicorn app.main:app --reload --port 8000
```

### Database Migrations

```bash
aerich migrate --name "description"  # Create migration
aerich upgrade                       # Apply migration
# or
make migrate
```

### Code Quality

```bash
black app/ tests/      # Format code
isort app/ tests/      # Sort imports
mypy app/              # Type checking
```

---

## 📁 Estructura del Proyecto

```
.
├── app/
│   ├── api/                  # HTTP layer
│   │   ├── middleware/       # Middleware (idempotency, context)
│   │   ├── app.py            # FastAPI app configuration
│   │   └── *_endpoint.py     # API endpoints
│   │
│   ├── bp/                   # Business logic (vertical slices)
│   │   ├── domain/           # Domain models
│   │   ├── repository/       # Repository interfaces
│   │   └── *_usecase.py      # Use cases
│   │
│   ├── core/                 # Core configuration
│   │   ├── config.py         # Application settings
│   │   ├── database.py       # Database setup
│   │   └── observability.py  # Logging & tracing setup
│   │
│   ├── infrastructure/       # Infrastructure services
│   │   ├── health/           # Health checks
│   │   │   ├── health_checker.py
│   │   │   └── system_monitor.py
│   │   └── metrics/          # Prometheus metrics
│   │       └── prometheus.py
│   │
│   ├── data/                 # Repository implementations
│   │   └── datasources/      # Data sources
│   │
│   ├── di/                   # Dependency injection
│   └── schemas/              # Pydantic schemas
│
├── migrations/              # Database migrations
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── Makefile                 # Common commands
└── requirements.txt         # Python dependencies
```

## 📈 SLOs

| Metric | Target | Prometheus Query |
|--------|--------|------------------|
| P95 Latency | < 100ms | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| Success Rate | > 99% | `rate(signup_requests_total{status="success"}[5m])` |
| Duplicates | 0 | `signup_duplicates_total` |
| Availability | > 99.9% | Health checks |


## 🔐 Security

### Password Requirements
- Minimum 8 characters
- 1 uppercase, 1 lowercase, 1 digit
- Hashed with bcrypt (cost factor 12)

### Required Headers
- `Idempotency-Key` - Prevents duplicate operations
- `X-Request-Id` - Request tracing

### Environment Variables

See `.env.sample` for all required variables. Key ones:

```bash
SECRET_KEY=<generate-with-openssl-rand-hex-32>
DB_DSN=postgres://user:password@host:5432/db
ENABLE_TRACING=true
LOG_LEVEL=INFO
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture and design patterns
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guidelines for contributing

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- OpenTelemetry for observability standards
- The Python community


