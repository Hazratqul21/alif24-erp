from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(50))
    old_values = Column(Text)
    new_values = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    tenant_id = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_level = Column(String(10), nullable=False, index=True)
    message = Column(Text, nullable=False)
    channel = Column(String(50))
    context = Column(Text)
    file = Column(String(300))
    line = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
