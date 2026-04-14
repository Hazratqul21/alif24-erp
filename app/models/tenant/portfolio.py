from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    file_url = Column(String(500))
    achievement_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")


class TeacherDevelopment(Base):
    __tablename__ = "teacher_development"

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    type = Column(String(50))
    description = Column(Text)
    certificate_url = Column(String(500))
    completion_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("Teacher")
