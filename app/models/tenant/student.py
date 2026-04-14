from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base, generate_uuid


class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    current_class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"))
    enrollment_date = Column(Date, nullable=False)
    status = Column(String(20), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="student")
    current_class = relationship("Class", foreign_keys=[current_class_id])
    enrollments = relationship("Enrollment", back_populates="student", lazy="selectin")
    grades = relationship("Grade", back_populates="student", lazy="dynamic")
    attendance_records = relationship("Attendance", back_populates="student", lazy="dynamic")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    enroll_date = Column(Date, nullable=False)
    leave_date = Column(Date)
    status = Column(String(20), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="enrollments")
    class_ = relationship("Class")
    academic_year = relationship("AcademicYear")
