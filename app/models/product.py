from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy import Boolean
from datetime import datetime

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    product_name = Column(String(150), nullable=False)
    hsn = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    variant = Column(String(100), nullable=False)
    color = Column(String(50), nullable=False)

    purchase_price = Column(Float)
    sale_price = Column(Float, nullable=False)
    tax_rate = Column(Float)

    stock_qty = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=0)

    description = Column(Text)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
