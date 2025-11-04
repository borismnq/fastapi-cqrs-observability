from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from app.core.config import settings


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=settings.password_min_length)
    display_name: str = Field(..., min_length=1, max_length=255)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < settings.password_min_length:
            raise ValueError(f"Password must be at least {settings.password_min_length} characters")
        
        has_upper = any(char.isupper() for char in value)
        has_lower = any(char.islower() for char in value)
        has_digit = any(char.isdigit() for char in value)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
            
        return value


class SignupResponse(BaseModel):
    id: UUID
    name: str
    email: str
    display_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):   
    id: UUID
    name: str
    email: str
    display_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
