"""Health check service for monitoring application status."""

import time
from typing import Dict, Any
from datetime import datetime
from tortoise import Tortoise
from loguru import logger

from .system_monitor import system_monitor


class HealthChecker:
    """Service for checking application health and readiness."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds."""
        return time.time() - self.start_time
    
    async def check_database(self) -> Dict[str, Any]:
        """
        Check database connectivity and health.
        
        Returns:
            Dict with status and message
        """
        try:
            conn = Tortoise.get_connection("default")
            await conn.execute_query("SELECT 1")
            
            return {
                "status": "healthy",
                "message": "Database connection is active"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get basic health status (liveness probe).
        
        This endpoint should always return 200 if the process is running.
        Used by orchestrators to determine if the container should be restarted.
        
        Returns:
            Dict with health status
        """
        uptime = self.get_uptime()
        
        return {
            "status": "healthy",
            "service": "signup-service",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": round(uptime, 2)
        }
    
    async def get_readiness_status(self) -> Dict[str, Any]:
        """
        Get detailed readiness status (readiness probe).
        
        Checks:
        - Database connectivity
        - System resources (CPU, memory, disk)
        
        Returns 'ready' if all checks pass, 'not_ready' otherwise.
        Used by load balancers to determine if traffic should be routed.
        
        Returns:
            Dict with readiness status and detailed checks
        """
        db_status = await self.check_database()
        system_metrics = system_monitor.get_all_metrics()
        uptime = self.get_uptime()
        
        # Determine overall readiness
        is_ready = (
            db_status["status"] == "healthy" and
            system_monitor.is_healthy()
        )
        
        return {
            "status": "ready" if is_ready else "not_ready",
            "service": "signup-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "checks": {
                "database": db_status,
                "system": system_metrics
            },
            "endpoints": {
                "signup": "POST /signup",
                "get_user": "GET /users/{user_id}",
                "health": "GET /health",
                "ready": "GET /ready",
                "metrics": "GET /metrics"
            }
        }


# Global instance
health_checker = HealthChecker()
