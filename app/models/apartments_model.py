from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, func, Enum
from .base import Base
from sqlalchemy.orm import relationship

class Apartments(Base):
    __tablename__ = 'apartments'

    id = Column(Integer, primary_key=True, nullable=False,index=False)
    landlord_id = Column(
        Integer,
        ForeignKey('landlords.id'),
        nullable=False
    ) 
    name = Column(String(255), nullable=False)
    image_url = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=True)

    
    landlord = relationship("Landlords", back_populates="apartments")
