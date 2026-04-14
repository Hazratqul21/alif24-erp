from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    room_number = Column(String(20), unique=True)
    capacity = Column(Integer, default=30)
    room_type = Column(String(50))
    building = Column(String(100))
    equipment = Column(Text)
    is_available = Column(Boolean, default=True)


class RoomBooking(Base):
    __tablename__ = "room_bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    booked_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    booking_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    purpose = Column(String(300))
    status = Column(String(20), default="confirmed")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room")
    user = relationship("User")
