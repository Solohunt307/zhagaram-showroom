from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=True)
    showroom = relationship("Showroom", back_populates="users")