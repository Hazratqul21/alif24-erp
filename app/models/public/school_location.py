from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class SchoolLocation(Base):
    __tablename__ = "school_locations"
    __table_args__ = {"schema": "public"}

    tenant_id = Column(Integer, ForeignKey("public.tenants.id"), primary_key=True)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    address = Column(Text)
    district = Column(String(100))
    region = Column(String(100))
    interlibrary_enabled = Column(Boolean, default=False)
    working_hours = Column(String(100))

    tenant = relationship("Tenant", back_populates="location")
