from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    calories = Column(Integer)
    has_allergens = Column(Boolean, default=False)
    allergens = Column(String(500))
    is_active = Column(Boolean, default=True)


class DailyMenu(Base):
    __tablename__ = "daily_menu"

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String(20), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)

    item = relationship("MenuItem")


class MealOrder(Base):
    __tablename__ = "meal_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    order_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String(20), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="ordered")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    item = relationship("MenuItem")


class StudentDietaryRestriction(Base):
    __tablename__ = "student_dietary_restrictions"

    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    restriction_type = Column(String(100), primary_key=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
