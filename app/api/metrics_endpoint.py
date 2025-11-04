from fastapi import APIRouter
from app.infrastructure.metrics import get_metrics_data

router = APIRouter(prefix="", tags=["observability"])


@router.get("/metrics")
async def metrics():
    """
    Expose Prometheus metrics.
    
    Returns metrics in Prometheus text format for scraping.
    """
    return get_metrics_data()