from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    document_number = Column(String(50))
    type = Column(String(50))
    category = Column(String(50))
    content = Column(Text)
    file_url = Column(String(500))
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))
    issue_date = Column(Date)
    effective_date = Column(Date)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploader = relationship("User", foreign_keys=[uploaded_by])
    signatories = relationship("DocumentSignatory", back_populates="document", lazy="selectin")
    versions = relationship("DocumentVersion", back_populates="document", lazy="dynamic")


class DocumentSignatory(Base):
    __tablename__ = "document_signatories"

    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    signature_status = Column(String(20), default="pending")
    signed_at = Column(Date)
    comments = Column(Text)

    document = relationship("Document", back_populates="signatories")
    user = relationship("User")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_url = Column(String(500))
    changes = Column(Text)
    uploaded_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="versions")
