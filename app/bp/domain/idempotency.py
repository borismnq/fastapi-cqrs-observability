from tortoise import fields
from tortoise.models import Model
from datetime import datetime, timedelta, timezone


class IdempotencyKey(Model):
    """Store idempotency keys to prevent duplicate operations."""
    
    key = fields.CharField(max_length=255, pk=True, index=True)
    endpoint = fields.CharField(max_length=255)
    request_hash = fields.CharField(max_length=64)
    response_status = fields.IntField()
    response_body = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()
    
    class Meta:
        table = "idempotency_keys"
        
    def __str__(self):
        return f"IdempotencyKey(key={self.key}, endpoint={self.endpoint})"
    
    @classmethod
    async def create_with_expiration(cls, key: str, endpoint: str, request_hash: str, 
                                  response_status: int, response_body: dict, 
                                  ttl_hours: int = 24):
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        return await cls.create(
            key=key,
            endpoint=endpoint,
            request_hash=request_hash,
            response_status=response_status,
            response_body=response_body,
            expires_at=expires_at,
        )
