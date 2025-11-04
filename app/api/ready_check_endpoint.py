from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.infrastructure.health import health_checker

router = APIRouter(prefix="", tags=["health"])


@router.get("/ready")
async def ready_check():
    """
    Readiness probe - checks if the application is ready to serve traffic.
    
    Verifies:
    - Database connectivity
    - System resources (CPU, memory, disk)
    - All critical dependencies
    
    Returns 200 if ready, 503 if not ready.
    Used by load balancers to route traffic only to ready instances.
    """
    readiness_status = await health_checker.get_readiness_status()
    
    # Return 503 if not ready
    if readiness_status["status"] != "ready":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=readiness_status
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=readiness_status
    )
    