import pytest
import asyncio
from fastapi.testclient import TestClient
from tortoise import Tortoise
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import uuid
from app.core.config import settings
from app.main import app as original_app
from app.core.database import TORTOISE_ORM
import os

os.environ["ENABLE_TRACING"] = "False"
# Override database settings for tests
settings.db_dsn = "sqlite://:memory:"

# Update the TORTOISE_ORM config with test settings
TORTOISE_ORM["connections"]["default"] = settings.db_dsn

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db():
    """Initialize and clean up the test database for each test."""
    # Initialize the database with a new in-memory SQLite database
    test_config = TORTOISE_ORM.copy()
    test_config["connections"]["default"] = "sqlite://:memory:"
    
    # Initialize Tortoise with the test config
    await Tortoise.init(config=test_config)
    await Tortoise.generate_schemas()
    
    yield
    
    # Clean up
    if Tortoise._inited:
        await Tortoise.close_connections()
        await Tortoise._drop_databases()

@pytest.fixture(scope="function")
async def app(db):
    """Create a test FastAPI app with a test lifespan for each test."""
    # Create a new FastAPI app with a test lifespan
    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        # Database is already initialized by the db fixture
        yield {}
    
    # Create a new FastAPI app with our test lifespan
    test_app = FastAPI(lifespan=test_lifespan)
    
    # Include all routers from the original app
    for route in original_app.routes:
        test_app.router.routes.append(route)
    
    # Include all exception handlers
    for exc_type, handler in original_app.exception_handlers.items():
        test_app.add_exception_handler(exc_type, handler)
    
    # Include all middleware
    for middleware in original_app.user_middleware:
        # Get the middleware class and its init parameters
        middleware_cls = middleware.cls
        
        # The middleware options are stored differently in different FastAPI versions
        if hasattr(middleware, 'options'):
            # For older FastAPI versions
            test_app.add_middleware(middleware_cls, **middleware.options)
        else:
            # For newer FastAPI versions, the options are passed directly to the middleware
            try:
                test_app.add_middleware(middleware_cls)
            except TypeError:
                # If the middleware requires specific arguments, we'll need to handle them
                if middleware_cls.__name__ == 'IdempotencyMiddleware':
                    test_app.add_middleware(middleware_cls, header_name='X-Idempotency-Key')
                else:
                    # For other middleware, try to initialize with empty args
                    test_app.add_middleware(middleware_cls)
    
    return test_app

@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app with request state initialized."""
    # Create a custom test client that adds request state
    from fastapi.testclient import TestClient as _TestClient
    
    class CustomTestClient(_TestClient):
        def request(self, method, url, **kwargs):
            # Ensure headers is a dictionary
            headers = dict(kwargs.get('headers') or {})
            
            # Generate request_id and correlation_id if not provided
            if not headers.get('X-Request-ID'):
                headers['X-Request-ID'] = str(uuid.uuid4())
            if not headers.get('X-Correlation-ID'):
                headers['X-Correlation-ID'] = str(uuid.uuid4())
                
            kwargs['headers'] = headers
            return super().request(method, url, **kwargs)
    
    with CustomTestClient(app) as test_client:
        yield test_client
