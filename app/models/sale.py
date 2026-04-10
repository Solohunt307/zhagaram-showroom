from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), unique=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    status = Column(String(20), default="ACTIVE")

    quantity = Column(Integer)
    order_amount = Column(Float)
    paid_amount = Column(Float)
    balance_amount = Column(Float)

    payment_type = Column(String(50))
    invoice_number = Column(String(50), unique=True)

    sale_date = Column(Date)

    received_by = Column(String(100))
    notes = Column(Text)

    gst_percent = Column(Float)
    tax_amount = Column(Float)
    final_amount = Column(Float)

    # ---------- RELATIONSHIPS ----------

    product = relationship("Product")
    customer = relationship("Customer")

    payments = relationship(
        "SalePayment",
        back_populates="sale",
        cascade="all, delete"
    )
