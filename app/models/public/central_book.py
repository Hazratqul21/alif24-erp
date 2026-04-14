from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class CentralBook(Base):
    __tablename__ = "central_books"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    isbn = Column(String(20), unique=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(300), nullable=False, index=True)
    publisher = Column(String(300))
    year = Column(Integer)
    genre = Column(String(100))
    language = Column(String(50), default="uz")
    pages = Column(Integer)
    description = Column(Text)
    cover_image = Column(String(500))
    added_by_tenant = Column(Integer)
    added_by_user = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
