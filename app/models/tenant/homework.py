from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Homework(Base):
    __tablename__ = "homework"

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="SET NULL"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    due_date = Column(Date, nullable=False)
    attachments = Column(JSON, default=lambda: [])
    max_score = Column(Integer, default=100)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    teacher = relationship("Teacher")
    class_ = relationship("Class")
    subject = relationship("Subject")
    submissions = relationship("HomeworkSubmission", back_populates="homework", lazy="dynamic")


class HomeworkSubmission(Base):
    __tablename__ = "homework_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    homework_id = Column(Integer, ForeignKey("homework.id", ondelete="CASCADE"), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    file_url = Column(String(500))
    content = Column(Text)
    grade = Column(Integer)
    feedback = Column(Text)
    graded_at = Column(DateTime(timezone=True))

    student = relationship("Student")
    homework = relationship("Homework", back_populates="submissions")
