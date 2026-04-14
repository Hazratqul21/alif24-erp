from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    venue = Column(String(200))
    organizer = Column(String(200))
    max_participants = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    participants = relationship("CompetitionParticipant", back_populates="competition", lazy="selectin")


class CompetitionParticipant(Base):
    __tablename__ = "competition_participants"

    competition_id = Column(Integer, ForeignKey("competitions.id", ondelete="CASCADE"), primary_key=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    status = Column(String(20), default="registered")
    score = Column(Numeric(8, 2))
    rank = Column(Integer)
    certificate_url = Column(String(500))

    competition = relationship("Competition", back_populates="participants")
    student = relationship("Student")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    start_time = Column(String(10))
    end_time = Column(String(10))
    venue = Column(String(200))
    target_audience = Column(String(100))
    status = Column(String(20), default="upcoming")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    registrations = relationship("EventRegistration", back_populates="event", lazy="selectin")


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    registration_date = Column(Date)
    attendance_status = Column(String(20), default="registered")

    event = relationship("Event", back_populates="registrations")
    user = relationship("User")
