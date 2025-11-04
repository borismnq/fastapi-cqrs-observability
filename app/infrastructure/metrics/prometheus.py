"""Prometheus metrics definitions for the application."""

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


# HTTP Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)


# Business Metrics - Signup
signup_requests_total = Counter(
    "signup_requests_total",
    "Total signup requests",
    ["status"],
)

signup_duplicates_total = Counter(
    "signup_duplicates_total",
    "Total duplicate signup attempts",
)


# Idempotency Metrics
idempotency_hits_total = Counter(
    "idempotency_hits_total",
    "Total idempotency key cache hits",
    ["endpoint"],
)


def get_metrics_data() -> Response:
    """
    Generate Prometheus metrics in text format.
    
    Returns:
        Response with metrics in Prometheus format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
