from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    subdomain = Column(String(100), unique=True, index=True)
    domain = Column(String(200), unique=True)
    schema_name = Column(String(100), unique=True)
    name = Column(String(255), nullable=False)
    logo = Column(String(500))
    address = Column(Text)
    region = Column(String(100))
    phone = Column(String(20))
    email = Column(String(255))
    admin_email = Column(String(255))
    admin_phone = Column(String(30))

    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    subscription_end = Column(Date)
    plan_id = Column(Integer, ForeignKey("public.plans.id", ondelete="SET NULL"), nullable=True)

    max_users = Column(Integer, default=100)
    max_students = Column(Integer, default=500)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    plan = relationship("Plan", back_populates="tenants", lazy="selectin")
    location = relationship("SchoolLocation", back_populates="tenant", uselist=False, lazy="selectin")


class SuperAdmin(Base):
    __tablename__ = "super_admins"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    totp_secret = Column(String(100))
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
