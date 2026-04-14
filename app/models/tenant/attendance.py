from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    attendance_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="present")
    reason = Column(Text)
    check_in_time = Column(Time)
    check_out_time = Column(Time)
    marked_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendance_records")
    schedule = relationship("Schedule")
    marker = relationship("User", foreign_keys=[marked_by])
