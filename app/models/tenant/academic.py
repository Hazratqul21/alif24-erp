from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    grade_level = Column(String(10), nullable=False)
    section = Column(String(10))
    capacity = Column(Integer, default=30)
    homeroom_teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    homeroom_teacher = relationship("Teacher", foreign_keys=[homeroom_teacher_id])
    students = relationship("Student", foreign_keys="Student.current_class_id", lazy="dynamic")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    credit_hours = Column(Integer, default=1)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TeacherSubject(Base):
    __tablename__ = "teacher_subjects"

    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), primary_key=True)

    teacher = relationship("Teacher", back_populates="subjects")
    subject = relationship("Subject")
    academic_year = relationship("AcademicYear")
