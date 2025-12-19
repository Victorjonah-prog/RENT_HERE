from pydantic import BaseModel, Field, validator
from datetime import datetime
from ..enums import Gender

class User(BaseModel):
    name: str = Field(min_length=2)
    phone: str
    email: str
    gender: Gender
    location: str

