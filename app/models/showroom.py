# app/models/showroom.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Showroom(Base):
    __tablename__ = "showrooms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), unique=True, nullable=False)
    location = Column(String(150), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 🔗 Relationships
    users = relationship("User", back_populates="showroom")

    def __repr__(self):
        return f"<Showroom {self.name}>"
