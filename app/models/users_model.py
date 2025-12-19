from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, func, Enum
from .base import Base
from ..enums import Gender
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False,index=False)
    name = Column(String(50),  nullable=False)
    phone = Column(String(15), nullable=True, unique=True)
    email= Column(String(100), unique=True, nullable=False, index=True)
    gender = Column(String(10), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    landlord_profile = relationship("Landlords", back_populates="user", uselist=False)
    tenant_profile = relationship("Tenants", back_populates="user", uselist=False)  

 
    
