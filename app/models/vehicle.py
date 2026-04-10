from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))

    model_name = Column(String(150), nullable=False)
    variant = Column(String(150))
    color = Column(String(150))

    stock_qty = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=2)

    is_active = Column(Boolean, default=True)

    showroom = relationship("Showroom")
