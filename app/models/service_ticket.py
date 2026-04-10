from sqlalchemy import Column, Integer, String, Date, Text, DECIMAL, ForeignKey, TIMESTAMP
from app.core.database import Base
from datetime import datetime


class ServiceTicket(Base):

    __tablename__ = "service_tickets"

    id = Column(Integer, primary_key=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"))

    ticket_code = Column(String(50))

    customer_name = Column(String(150))
    product_name = Column(String(150))
    product_description = Column(Text)

    complaint = Column(Text)

    mobile = Column(String(20))
    technician = Column(String(150))

    resolved_complaint = Column(Text)
    unresolved_complaint = Column(Text)

    bill_no = Column(String(50))
    received_by = Column(String(100))

    service_completed_date = Column(Date)

    service_cost = Column(DECIMAL(10, 2))
    amount_paid = Column(DECIMAL(10, 2))
    balance = Column(DECIMAL(10, 2))

    payment_mode = Column(String(20))
    payment_date = Column(Date)

    attachment_path = Column(String(255))

    status = Column(String(30), default="OPEN")

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    closed_at = Column(Date)
