from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApartmentResponse(BaseModel):
    id: int
    landlord_id: int
    name: str
    image_url: str
    address: str
    description: str
    price: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
