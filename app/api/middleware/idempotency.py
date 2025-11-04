import hashlib
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from app.bp.domain import IdempotencyKey
from app.infrastructure.metrics import idempotency_hits_total
from datetime import datetime, timezone


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle POST requests with Idempotency-Key header"""
    
    IDEMPOTENT_METHODS = {"POST"}
    
    async def dispatch(self, request: Request, call_next):
        if request.method not in self.IDEMPOTENT_METHODS:
            return await call_next(request)
        
        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)
        
        body = await request.body()
        request_hash = hashlib.sha256(body).hexdigest()
        
        # restore body
        async def receive():
            return {"type": "http.request", "body": body}
        
        request._receive = receive
        
        existing = await IdempotencyKey.get_or_none(key=idempotency_key)
        
        if existing:
            # check expiration
            if existing.expires_at < datetime.now(timezone.utc):
                logger.info(f"Idempotency key expired: {idempotency_key}")
                await existing.delete()
            else:
                if existing.request_hash != request_hash:
                    logger.warning(
                        f"Idempotency key reused with different payload: {idempotency_key}"
                    )
                    return Response(
                        content=json.dumps({
                            "error": "Idempotency key conflict",
                            "detail": "Same key used with different request body"
                        }),
                        status_code=422,
                        media_type="application/json",
                    )
                
                logger.info(f"Idempotency hit: {idempotency_key}")
                # metrics
                idempotency_hits_total.labels(endpoint=request.url.path).inc()
                
                # Response headers
                headers = {
                    "X-Idempotency-Hit": "true"
                }                
                # Add request_id and correlation_id if available
                if hasattr(request.state, 'request_id'):
                    headers["X-Request-Id"] = request.state.request_id
                if hasattr(request.state, 'correlation_id'):
                    headers["X-Correlation-Id"] = request.state.correlation_id
                
                return Response(
                    content=json.dumps(existing.response_body),
                    status_code=existing.response_status,
                    media_type="application/json",
                    headers=headers,
                )
        
        response = await call_next(request)
        
        # create idempotency data on success response
        if 200 <= response.status_code < 300:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            try:
                response_data = json.loads(response_body)
                
                await IdempotencyKey.create_with_expiration(
                    key=idempotency_key,
                    endpoint=request.url.path,
                    request_hash=request_hash,
                    response_status=response.status_code,
                    response_body=response_data,
                    ttl_hours=24,
                )
                
                logger.info(f"Stored idempotency key: {idempotency_key}")
                
            except json.JSONDecodeError:
                logger.warning(f"Could not parse response body for idempotency storage")
            
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        
        return response
