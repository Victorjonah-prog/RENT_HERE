from pydantic import BaseModel, Field, validator
from datetime import datetime

class Tenants(BaseModel):
    user_id: int
    created_at: datetime = None
    updated_at: datetime = None

