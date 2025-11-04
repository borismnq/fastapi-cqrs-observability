from tortoise import fields
from tortoise.models import Model


class User(Model):   
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True, index=True)
    password_hash = fields.CharField(max_length=255)
    display_name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "users"
        
    def __str__(self):
        return f"User(id={self.id}, email={self.email})"


class UserReadModel(Model):    
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, index=True)
    display_name = fields.CharField(max_length=255)
    created_at = fields.DatetimeField()
    
    class Meta:
        table = "users_read_model"
        
    def __str__(self):
        return f"UserReadModel(id={self.id}, email={self.email})"
