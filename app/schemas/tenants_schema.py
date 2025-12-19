from pydantic import BaseModel, Field, validator
from datetime import datetime

class Tenants(BaseModel):
    user_id: int
    email: str
    created_at: datetime = None
    updated_at: datetime = None

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v

