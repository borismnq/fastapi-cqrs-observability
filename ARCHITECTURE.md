# Architecture Documentation

## Overview

This project implements a production-ready FastAPI backend using CQRS pattern, idempotency, and comprehensive observability.

## Architecture Patterns

### 1. Layered Architecture

The application follows a clean layered architecture:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - Endpoints, Middleware, Routes    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Business Logic Layer (bp/)     │
│  - Use Cases, Domain Models         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Infrastructure Layer             │
│  - Health Checks, Metrics           │
│  - System Monitoring                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Data Layer (Repository)        │
│  - Database Access, ORM             │
└─────────────────────────────────────┘
```

**Key Principles**:
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Rule**: Dependencies point inward (API → Business → Data)
- **Testability**: Easy to mock and test each layer independently

### 2. CQRS (Command Query Responsibility Segregation)

The system separates read and write operations:

```
┌─────────────────────────────────────┐
│         FastAPI Application         │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Command (Write) Side       │  │
│  │   - SignupUseCase            │  │
│  │   - UserCreateRepository     │  │
│  │   - Write to users table     │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   Query (Read) Side          │  │
│  │   - GetUserUseCase           │  │
│  │   - UserReadRepository       │  │
│  │   - Read from users_read     │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

**Benefits**:
- Optimized read and write models
- Better scalability
- Clear separation of concerns
- Easier to maintain and test

### 3. Vertical Slice Architecture

Each feature (slice) contains all layers:

```
bp/signup/
├── domain/          # Business logic
├── repository/      # Data access interfaces
└── usecase/         # Application logic
```

**Benefits**:
- High cohesion within features
- Low coupling between features
- Easy to add/remove features
- Clear boundaries

### 3. Dependency Injection

Using FastAPI's dependency injection system:

```python
@router.post("/signup")
async def signup(
    request: SignupRequest,
    usecase: SignupUseCase = Depends(get_signup_usecase)
):
    return await usecase.execute(request)
```

**Benefits**:
- Testability
- Loose coupling
- Easy to swap implementations

## Middleware Stack

Requests flow through middleware in this order:

```
1. RequestContext Middleware
   ↓ (adds request_id, correlation_id)
2. Idempotency Middleware
   ↓ (checks cache, prevents duplicates)
3. OpenTelemetry Instrumentation
   ↓ (traces, metrics)
4. Route Handler
   ↓
5. Use Case Execution
   ↓
6. Repository Layer
   ↓
7. Database
```

### Idempotency Middleware

Prevents duplicate operations using `Idempotency-Key` header:

```python
# First request
POST /signup
Idempotency-Key: abc-123
→ Creates user, caches response

# Duplicate request (within 24h)
POST /signup
Idempotency-Key: abc-123
→ Returns cached response, no DB write
```

**Implementation**:
- In-memory cache (can be replaced with Redis)
- 24-hour TTL
- Stores full response
- Thread-safe

## Database Schema

### Write Model (users table)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Read Model (users_read table)

```sql
CREATE TABLE users_read (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    created_at TIMESTAMP,
    -- Denormalized fields for fast reads
    INDEX idx_email (email)
);
```

**Synchronization**:
- Write operations update both tables in a transaction
- Read operations only query users_read
- Optimized for read-heavy workloads

## Observability Stack

### 1. Structured Logging

Using Loguru for structured logs:

```python
logger.info(
    "User created",
    user_id=user.id,
    email=user.email,
    request_id=request_id
)
```

**Output**:
```json
{
  "timestamp": "2025-11-04T16:00:00Z",
  "level": "INFO",
  "message": "User created",
  "user_id": "abc-123",
  "email": "user@example.com",
  "request_id": "req-456"
}
```

### 2. Metrics (Prometheus)

Custom metrics exposed at `/metrics`:

```python
# Counter
signup_requests_total.labels(status="success").inc()

# Histogram
http_request_duration_seconds.observe(duration)

# Gauge
active_connections.set(count)
```

**Key Metrics**:
- Request latency (P50, P95, P99)
- Request rate
- Error rate
- Duplicate attempts
- Idempotency cache hits

### 3. Distributed Tracing (Jaeger)

Using OpenTelemetry for traces:

```python
with tracer.start_as_current_span("signup_operation"):
    # Operation code
    with tracer.start_as_current_span("db_write"):
        # Database operation
```

**Trace Information**:
- Request flow across services
- Operation duration
- Error tracking
- Context propagation

## Health Checks

The application provides two types of health checks following Kubernetes best practices:

### 1. Liveness Probe (`/health`)

Checks if the application is alive and running:

```python
@router.get("/health")
async def health_check():
    """Returns 200 if service is alive."""
    return {
        "status": "healthy",
        "service": "signup-service",
        "uptime_seconds": uptime
    }
```

**Purpose**: 
- Determines if container should be restarted
- Always returns 200 if the process is running
- Does not check dependencies

**Use Case**: Kubernetes liveness probe

### 2. Readiness Probe (`/ready`)

Checks if the application is ready to serve traffic:

```python
@router.get("/ready")
async def ready_check():
    """Returns 200 if ready, 503 if not ready."""
    # Check database
    db_status = await check_database()
    
    # Check system resources
    system_metrics = get_system_metrics()
    
    # Return 503 if not ready
    if not is_ready:
        return JSONResponse(status_code=503, content=status)
```

**Checks Performed**:
- **Database connectivity**: Executes `SELECT 1` query
- **CPU usage**: Monitors current CPU utilization
- **Memory usage**: Checks available memory (fails if >95% used)
- **Disk usage**: Monitors disk space (fails if >95% used)

**Purpose**:
- Determines if traffic should be routed to this instance
- Returns 503 if dependencies are unavailable
- Used by load balancers

**Use Case**: Kubernetes readiness probe, load balancer health checks

### System Metrics

Using `psutil` to monitor:

```python
{
    "cpu": {
        "usage_percent": 15.2,
        "count": 8
    },
    "memory": {
        "total_mb": 16384,
        "available_mb": 8192,
        "used_percent": 50.0
    },
    "disk": {
        "total_gb": 500,
        "free_gb": 250,
        "used_percent": 50.0
    }
}
```

### Docker Compose Configuration

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Kubernetes Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Error Handling

Centralized error handling with custom exceptions:

```python
class DomainException(Exception):
    """Base exception for domain errors"""

class UserAlreadyExistsError(DomainException):
    """Raised when user email already exists"""

@app.exception_handler(DomainException)
async def domain_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

## Security

### Password Hashing

```python
# Using bcrypt with cost factor 12
password_hash = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt(rounds=12)
)
```

### Input Validation

Using Pydantic schemas:

```python
class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        # Custom validation logic
        return v
```

## Performance Considerations

### Database Optimization

1. **Indexes**: Email field indexed for fast lookups
2. **Connection Pooling**: Reuse database connections
3. **Read Replicas**: Separate read model for scaling

### Caching Strategy

1. **Idempotency Cache**: In-memory (24h TTL)
2. **Future**: Redis for distributed caching

### Async Operations

All I/O operations are async:

```python
async def create_user(self, user: User) -> User:
    await self.db.execute(query)
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
@pytest.mark.asyncio
async def test_signup_usecase():
    # Mock dependencies
    mock_repo = Mock(UserCreateRepository)
    usecase = SignupUseCase(mock_repo)
    
    # Test
    result = await usecase.execute(request)
    
    # Assert
    assert result.email == request.email
```

### Integration Tests

Test complete flows:

```python
@pytest.mark.asyncio
async def test_signup_endpoint(client):
    response = await client.post("/signup", json={
        "name": "Test",
        "email": "test@example.com",
        "password": "Test123!"
    })
    assert response.status_code == 201
```

### Load Tests

Using Locust for performance testing:

```python
class SignupUser(HttpUser):
    @task
    def signup(self):
        self.client.post("/signup", json=payload)
```

## Deployment

### Docker

Multi-stage build for optimization:

```dockerfile
# Build stage
FROM python:3.13-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.13-slim
COPY --from=builder /root/.local /root/.local
COPY app/ /app/
CMD ["uvicorn", "app.main:app"]
```

### Docker Compose

Services orchestration:

```yaml
services:
  app:        # FastAPI application
  postgres:   # Database
  jaeger:     # Tracing
  prometheus: # Metrics
```

## Future Improvements

1. **Event Sourcing**: Store all state changes as events
2. **Message Queue**: Async processing with RabbitMQ/Kafka
3. **API Gateway**: Centralized routing and auth
4. **Service Mesh**: Istio for advanced traffic management
5. **GraphQL**: Alternative API interface
6. **Kubernetes**: Container orchestration for production

## References

- [CQRS Pattern](https://martinfowler.com/bliki/CQRS.html)
- [Vertical Slice Architecture](https://jimmybogard.com/vertical-slice-architecture/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
