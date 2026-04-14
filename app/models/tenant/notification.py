from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    channel = Column(String(20), default="in_app")
    sender_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    is_broadcast = Column(Boolean, default=False)

    sender = relationship("User", foreign_keys=[sender_id])
    recipients = relationship("NotificationRecipient", back_populates="notification", lazy="selectin")


class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"

    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="CASCADE"), primary_key=True)
    recipient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipient_role = Column(String(50))
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))

    notification = relationship("Notification", back_populates="recipients")
    recipient = relationship("User")


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    subject = Column(String(300))
    sms_template = Column(Text)
    email_template = Column(Text)
    push_template = Column(Text)


class MessageThread(Base):
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_type = Column(String(20), default="direct")
    subject = Column(String(300))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="thread", lazy="dynamic")
    participants = relationship("ThreadParticipant", back_populates="thread", lazy="selectin")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)

    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User")


class ThreadParticipant(Base):
    __tablename__ = "thread_participants"

    thread_id = Column(Integer, ForeignKey("message_threads.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    thread = relationship("MessageThread", back_populates="participants")
    user = relationship("User")
