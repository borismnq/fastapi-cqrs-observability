from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.infrastructure.health import health_checker

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Liveness probe - checks if the application is running.
    
    Returns 200 if the service is alive, regardless of dependencies.
    Used by orchestrators (Kubernetes, Docker) to restart unhealthy containers.
    """
    health_status = await health_checker.get_health_status()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )