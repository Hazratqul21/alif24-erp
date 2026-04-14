from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_first_name = Column(String(100), nullable=False)
    applicant_last_name = Column(String(100), nullable=False)
    applicant_middle_name = Column(String(100))
    birth_date = Column(Date, nullable=False)
    gender = Column(String(10))
    parent_name = Column(String(200))
    parent_phone = Column(String(20), nullable=False)
    parent_email = Column(String(255))
    desired_grade = Column(String(10), nullable=False)
    previous_school = Column(String(300))
    documents = Column(JSON, default=lambda: [])
    status = Column(String(20), default="pending")
    notes = Column(Text)
    reviewed_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
