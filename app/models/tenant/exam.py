from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="SET NULL"))
    exam_date = Column(Date, nullable=False)
    duration_minutes = Column(Integer, default=60)
    total_marks = Column(Integer, default=100)
    exam_type = Column(String(50), default="written")
    questions = Column(JSON, default=lambda: [])
    is_online = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject")
    class_ = relationship("Class")
    teacher = relationship("Teacher")
    results = relationship("ExamResult", back_populates="exam", lazy="dynamic")


class ExamResult(Base):
    __tablename__ = "exam_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    marks_obtained = Column(Integer)
    grade = Column(String(5))
    remarks = Column(Text)
    answers = Column(JSON, default=lambda: [])
    submitted_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    exam = relationship("Exam", back_populates="results")
