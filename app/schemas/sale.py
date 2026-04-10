from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    amount: float
    payment_type: str
    received_by: str


class SaleCreate(BaseModel):
    customer_name: str
    address: str
    email: Optional[str]
    phone: str

    product_id: int
    quantity: int

    order_amount: float
    paid_amount: float
    payment_type: str

    sale_date: datetime

    received_by: str
    notes: Optional[str]

    payments: List[PaymentCreate] = []


class SaleOut(BaseModel):
    id: int
    invoice_number: str
    order_amount: float
    paid_amount: float
    balance_amount: float

    class Config:
        from_attributes = True
