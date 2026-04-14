from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PsychologicalTest(Base):
    __tablename__ = "psychological_tests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    questions_json = Column(JSON, default=lambda: [])
    total_score = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    test_id = Column(Integer, ForeignKey("psychological_tests.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer)
    result_level = Column(String(50))
    recommendations = Column(Text)
    test_date = Column(Date, nullable=False)
    conducted_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    test = relationship("PsychologicalTest")


class CounselingSession(Base):
    __tablename__ = "counseling_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    counselor_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    session_date = Column(Date, nullable=False)
    topic = Column(String(200))
    notes = Column(Text)
    status = Column(String(20), default="scheduled")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    counselor = relationship("User", foreign_keys=[counselor_id])


class BehaviorRecord(Base):
    __tablename__ = "behavior_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"))
    record_date = Column(Date, nullable=False)
    behavior_type = Column(String(50), nullable=False)
    description = Column(Text)
    action_taken = Column(Text)
    recorded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
