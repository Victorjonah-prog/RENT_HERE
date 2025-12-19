from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, func, Enum
from .base import Base
from ..enums import Gender
from sqlalchemy.orm import relationship

class Tenants(Base):
    __tablename__ = 'tenants'

    id = Column(Integer, primary_key=True, nullable=False,index=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    user = relationship("Users", back_populates="tenant_profile")