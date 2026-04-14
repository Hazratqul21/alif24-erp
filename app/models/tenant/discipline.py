from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class DisciplineIncident(Base):
    __tablename__ = "discipline_incidents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"))
    incident_date = Column(Date, nullable=False)
    incident_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="low")
    description = Column(Text, nullable=False)
    action_taken = Column(Text)
    parent_notified = Column(Integer, default=0)
    recorded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
