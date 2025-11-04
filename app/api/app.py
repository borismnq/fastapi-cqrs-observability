from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from app.core.database import init_db, close_db
from app.api.middleware.idempotency import IdempotencyMiddleware
from app.api.middleware.request_context import RequestContextMiddleware
from app.core.observability import setup_logging, setup_tracing

from . import health_check_endpoint
from . import metrics_endpoint
from . import ready_check_endpoint
from . import signup_endpoint
from . import get_user_endpoint


# handles init and close db
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Database connections closed")



def create_app():
    setup_logging()
    
    app = FastAPI(
        title="Users Signup",
        description="Signup users service with idempotency, observability, and CQRS",
        version="1.0.0",
        lifespan=lifespan,
    )
    # endpoints
    app.include_router(router=signup_endpoint.router)
    app.include_router(router=get_user_endpoint.router)
    app.include_router(router=health_check_endpoint.router)
    app.include_router(router=ready_check_endpoint.router)
    app.include_router(router=metrics_endpoint.router)
    # middlewares
    app.add_middleware(IdempotencyMiddleware)
    app.add_middleware(RequestContextMiddleware)

    setup_tracing(app)
    
    return app
