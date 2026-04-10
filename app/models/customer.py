from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import Boolean
from datetime import datetime

from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    name = Column(String(150), nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(150))
    phone = Column(String(30), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
