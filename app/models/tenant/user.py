from sqlalchemy import Column, String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base, generate_uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    birth_date = Column(Date)
    gender = Column(String(10))
    avatar = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    alif24_user_id = Column(String(20), index=True)

    totp_secret = Column(String(100))
    totp_enabled = Column(Boolean, default=False)

    refresh_token = Column(Text)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    roles = relationship("UserRole", back_populates="user", lazy="selectin")
    student = relationship("Student", back_populates="user", uselist=False, lazy="selectin")
    teacher = relationship("Teacher", back_populates="user", uselist=False, lazy="selectin")
    parent = relationship("Parent", back_populates="user", uselist=False, lazy="selectin")

    @property
    def full_name(self) -> str:
        parts = [self.last_name or "", self.first_name or "", self.middle_name or ""]
        return " ".join(p for p in parts if p).strip()
