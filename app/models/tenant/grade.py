from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GradeType(Base):
    __tablename__ = "grade_types"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    weight_percent = Column(Integer, default=100)


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="SET NULL"))
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    grade_type_id = Column(Integer, ForeignKey("grade_types.id", ondelete="SET NULL"))
    grade_value = Column(Integer, nullable=False)
    max_grade = Column(Integer, default=100)
    comment = Column(Text)
    grade_date = Column(Date, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject")
    teacher = relationship("Teacher")
    grade_type = relationship("GradeType")


class ReportCard(Base):
    __tablename__ = "report_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    semester = Column(Integer, nullable=False)
    gpa = Column(Numeric(4, 2))
    teacher_comments = Column(Text)
    principal_comments = Column(Text)
    issue_date = Column(Date)
    pdf_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    academic_year = relationship("AcademicYear")
