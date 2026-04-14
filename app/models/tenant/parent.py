from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base, generate_uuid


class Parent(Base):
    __tablename__ = "parents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    occupation = Column(String(200))
    workplace = Column(String(300))
    relationship_type = Column(String(20))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="parent")
    children = relationship("ParentChild", back_populates="parent", lazy="selectin")


class ParentChild(Base):
    __tablename__ = "parent_children"

    parent_id = Column(String(36), ForeignKey("parents.id", ondelete="CASCADE"), primary_key=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    relationship_type = Column(String(20), default="parent")

    parent = relationship("Parent", back_populates="children")
    student = relationship("Student")
