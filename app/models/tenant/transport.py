from sqlalchemy import Column, Integer, String, Date, Time, DateTime, ForeignKey, Numeric, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bus_number = Column(String(20), unique=True, nullable=False)
    license_plate = Column(String(20))
    capacity = Column(Integer, default=40)
    driver_name = Column(String(200))
    driver_phone = Column(String(20))
    route_name = Column(String(200))
    is_active = Column(Boolean, default=True)


class BusStop(Base):
    __tablename__ = "bus_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="CASCADE"), nullable=False)
    stop_name = Column(String(200), nullable=False)
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    arrival_time = Column(Time)
    departure_time = Column(Time)
    order_index = Column(Integer, default=0)

    bus = relationship("Bus")


class BusSubscription(Base):
    __tablename__ = "bus_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="CASCADE"), nullable=False)
    stop_id = Column(Integer, ForeignKey("bus_stops.id", ondelete="SET NULL"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    monthly_fee = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default="active")

    student = relationship("Student")
    bus = relationship("Bus")
    stop = relationship("BusStop")


class BusTracking(Base):
    __tablename__ = "bus_tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    speed = Column(Float, default=0)
    status = Column(String(20), default="moving")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    bus = relationship("Bus")
