from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    quantity = Column(Integer)
    color = Column(String(50))

    amount = Column(Float)
    payment_mode = Column(String(130))
    shipment_mode = Column(String(100))

    notes = Column(Text)

    purchase_date = Column(Date)

    file_path = Column(String(255))

    # -----------------------------
    # RELATIONSHIPS
    # -----------------------------

    product = relationship("Product")
    vendor = relationship("Vendor")
