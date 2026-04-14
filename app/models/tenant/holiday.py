from sqlalchemy import Column, Integer, String, Date, Boolean
from app.core.database import Base


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False)
    type = Column(String(50), default="public")
    is_annual = Column(Boolean, default=False)
