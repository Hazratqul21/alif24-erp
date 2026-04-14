from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SchoolBook(Base):
    __tablename__ = "school_books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    central_book_id = Column(Integer, nullable=False, index=True)
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    location = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BookLoan(Base):
    __tablename__ = "book_loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    school_book_id = Column(Integer, ForeignKey("school_books.id", ondelete="CASCADE"), nullable=False)
    loan_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    status = Column(String(20), default="borrowed")
    fine_amount = Column(Numeric(10, 2), default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    school_book = relationship("SchoolBook")


class InterlibraryRequest(Base):
    __tablename__ = "interlibrary_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    source_school_id = Column(Integer, nullable=False)
    target_school_id = Column(Integer, nullable=False)
    central_book_id = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    pickup_date = Column(Date)
    pickup_time_slot = Column(String(50))
    return_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))

    student = relationship("Student")
