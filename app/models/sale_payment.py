from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class SalePayment(Base):
    __tablename__ = "sale_payments"

    id = Column(Integer, primary_key=True)

    sale_id = Column(Integer, ForeignKey("sales.id"))

    amount = Column(Float)
    payment_type = Column(String(50))
    received_by = Column(String(100))

    paid_at = Column(DateTime, default=datetime.utcnow)

    sale = relationship("Sale", back_populates="payments")
