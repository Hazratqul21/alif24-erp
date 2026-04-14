from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    price_monthly = Column(Numeric(12, 2), default=0)
    price_yearly = Column(Numeric(12, 2), default=0)
    max_users = Column(Integer, default=100)
    max_students = Column(Integer, default=500)
    max_teachers = Column(Integer, default=50)

    has_library = Column(Boolean, default=True)
    has_transport = Column(Boolean, default=False)
    has_canteen = Column(Boolean, default=False)
    has_medical = Column(Boolean, default=True)
    has_psychology = Column(Boolean, default=False)
    has_interlibrary = Column(Boolean, default=False)
    has_competitions = Column(Boolean, default=True)
    has_portfolio = Column(Boolean, default=False)
    has_surveys = Column(Boolean, default=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenants = relationship("Tenant", back_populates="plan")
