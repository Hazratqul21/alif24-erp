from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    questions = Column(JSON, default=lambda: [])
    target_roles = Column(JSON, default=lambda: [])
    is_anonymous = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    responses = relationship("SurveyResponse", back_populates="survey", lazy="dynamic")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    respondent_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    answers = Column(JSON, default=lambda: [])
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    survey = relationship("Survey", back_populates="responses")
