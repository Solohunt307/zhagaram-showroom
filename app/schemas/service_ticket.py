from pydantic import BaseModel
from typing import Optional
from datetime import date


class ServiceTicketCreate(BaseModel):

    customer_name: Optional[str]
    product_name: Optional[str]
    product_description: Optional[str]

    complaint: Optional[str]

    mobile: Optional[str]
    technician: Optional[str]

    resolved_complaint: Optional[str]
    unresolved_complaint: Optional[str]
    status: Optional[str] = "OPEN"

    bill_no: Optional[str]
    received_by: Optional[str]

    service_completed_date: Optional[date]

    service_cost: Optional[float]
    amount_paid: Optional[float]
    balance: Optional[float]

    payment_mode: Optional[str]
    payment_date: Optional[date]


class ServiceTicketOut(ServiceTicketCreate):

    id: int
    ticket_code: str
    status: str

    class Config:
        from_attributes = True
