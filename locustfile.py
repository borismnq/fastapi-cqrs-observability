"""
Load testing with Locust.

Usage:
    locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 10 --run-time 2m
"""

from locust import HttpUser, task, between
import uuid


class SignupUser(HttpUser):
    """Simulated user performing signup operations."""
    
    wait_time = between(1, 3)
    
    @task(3)
    def signup(self):
        """Create a new user with unique email."""
        email = f"load-{uuid.uuid4()}@example.com"
        
        self.client.post(
            "/signup",
            json={
                "name": "Load Test User",
                "email": email,
                "password": "S3guro!123",
                "display_name": "Load Test"
            },
            headers={
                "Idempotency-Key": str(uuid.uuid4())
            }
        )
    
    @task(1)
    def health_check(self):
        """Check service health."""
        self.client.get("/health")
