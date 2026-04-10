from pydantic import BaseModel
from typing import List


class AccountingSummary(BaseModel):

    total_purchases: int
    total_sales: int

    total_purchase_amount: float
    total_sales_amount: float

    total_expenses: float

    net_profit: float


class InvoiceFilter(BaseModel):
    from_date: str
    to_date: str
    from_invoice: int
    to_invoice: int
