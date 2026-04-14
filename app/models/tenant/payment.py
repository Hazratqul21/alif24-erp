from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String(36), ForeignKey("parents.id", ondelete="SET NULL"))
    amount = Column(Numeric(12, 2), nullable=False)
    payment_type = Column(String(50), nullable=False)
    payment_date = Column(Date)
    due_date = Column(Date)
    status = Column(String(20), default="pending")
    transaction_id = Column(String(100), unique=True)
    payment_method = Column(String(50))
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    parent = relationship("Parent")


class PaymentPlan(Base):
    __tablename__ = "payment_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    frequency = Column(String(20), default="monthly")
    description = Column(Text)


class StudentPaymentPlan(Base):
    __tablename__ = "student_payment_plans"

    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    plan_id = Column(Integer, ForeignKey("payment_plans.id", ondelete="CASCADE"), primary_key=True)
    discount_percent = Column(Numeric(5, 2), default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    student = relationship("Student")
    plan = relationship("PaymentPlan")


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(String(50))
    is_required = Column(Integer, default=1)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"))
    invoice_number = Column(String(50), unique=True, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0)
    due_amount = Column(Numeric(12, 2), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    pdf_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student")
    payment = relationship("Payment")
