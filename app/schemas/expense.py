from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class ExpenseCreate(BaseModel):

    category: str
    description: Optional[str]
    amount: float
    expense_date: date


class ExpenseUpdate(ExpenseCreate):
    pass


class ExpenseOut(ExpenseCreate):

    id: int

    class Config:
        from_attributes = True


# ---------- BULK DAILY ----------

class ExpenseBulkCreate(BaseModel):

    items: List[ExpenseCreate]
