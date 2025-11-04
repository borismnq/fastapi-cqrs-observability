"""System resource monitoring using psutil."""

from typing import Dict, Any
import psutil
from loguru import logger


class SystemMonitor:
    """Monitor system resources (CPU, memory, disk)."""
    
    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU usage metrics."""
        try:
            return {
                "usage_percent": round(psutil.cpu_percent(interval=0.1), 2),
                "count": psutil.cpu_count()
            }
        except Exception as e:
            logger.error(f"Failed to get CPU metrics: {e}")
            return {"error": "Failed to retrieve CPU metrics"}
    
    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory usage metrics."""
        try:
            memory = psutil.virtual_memory()
            return {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "available_mb": round(memory.available / (1024 * 1024), 2),
                "used_percent": round(memory.percent, 2)
            }
        except Exception as e:
            logger.error(f"Failed to get memory metrics: {e}")
            return {"error": "Failed to retrieve memory metrics"}
    
    def get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk usage metrics."""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "used_percent": round(disk.percent, 2)
            }
        except Exception as e:
            logger.error(f"Failed to get disk metrics: {e}")
            return {"error": "Failed to retrieve disk metrics"}
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all system metrics."""
        return {
            "cpu": self.get_cpu_metrics(),
            "memory": self.get_memory_metrics(),
            "disk": self.get_disk_metrics()
        }
    
    def is_healthy(self) -> bool:
        """
        Check if system resources are healthy.
        
        Returns False if:
        - Memory usage > 95%
        - Disk usage > 95%
        """
        try:
            memory = self.get_memory_metrics()
            disk = self.get_disk_metrics()
            
            if "error" in memory or "error" in disk:
                return True  # Don't fail on metric errors
            
            if memory["used_percent"] > 95:
                logger.warning(f"Memory usage critical: {memory['used_percent']}%")
                return False
            
            if disk["used_percent"] > 95:
                logger.warning(f"Disk usage critical: {disk['used_percent']}%")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            return True  # Don't fail on errors


# Global instance
system_monitor = SystemMonitor()
