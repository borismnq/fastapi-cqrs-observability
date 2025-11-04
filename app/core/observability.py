"""Observability setup: logging and distributed tracing."""

import sys
from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from app.core.config import settings


# Service resource for tracing
resource = Resource(attributes={
    SERVICE_NAME: "signup-service"
})

def setup_logging():
    """
    Configure structured logging with Loguru.
    
    Sets up:
    - Console output with colored formatting
    - File output with JSON serialization (if enabled)
    - Log rotation and retention
    """
    if not settings.enable_logging:
        return
    
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level> | {extra}",
        level=settings.log_level,
        serialize=False,
    )
    
    # File logging (if enabled)
    if settings.enable_log_file:
        logger.add(
            "logs/app.log",
            rotation="100 MB",
            retention="10 days",
            level=settings.log_level,
            serialize=True,
        )


def setup_tracing(app):
    """
    Configure distributed tracing with Jaeger.
    
    Sets up:
    - OpenTelemetry tracer provider
    - Jaeger exporter
    - FastAPI instrumentation
    
    Args:
        app: FastAPI application instance
    """
    if not settings.enable_tracing:
        return
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.jaeger_agent_host,
        agent_port=settings.jaeger_agent_port,
    )
    
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    FastAPIInstrumentor.instrument_app(app)


def get_tracer(name: str):
    """
    Get a tracer instance for creating spans.
    
    Args:
        name: Name of the tracer (usually __name__)
    
    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)
