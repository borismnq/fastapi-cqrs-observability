import uuid
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from app.infrastructure.metrics import http_requests_total, http_request_duration_seconds


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to handle X-Request-Id, X-Correlation-Id headers and metrics."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
        correlation_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
        
        # Use request state to access headers from Idempotency middleware
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        
        with logger.contextualize(
            request_id=request_id,
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
        ):
            logger.info(f"Request started: {request.method} {request.url.path}")
            
            start_time = time.time()
            
            try:
                response = await call_next(request)
                duration = time.time() - start_time
                
                response.headers["X-Request-Id"] = request_id
                response.headers["X-Correlation-Id"] = correlation_id
                
                # metrics
                http_requests_total.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code,
                ).inc()
                
                # metrics
                http_request_duration_seconds.labels(
                    method=request.method,
                    endpoint=request.url.path,
                ).observe(duration)
                
                logger.info(
                    f"Request completed: {request.method} {request.url.path} "
                    f"status={response.status_code} duration={duration:.3f}s"
                )
                
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Request failed: {request.method} {request.url.path} "
                    f"error={str(e)} duration={duration:.3f}s"
                )
                
                http_requests_total.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=500,
                ).inc()
                
                raise
