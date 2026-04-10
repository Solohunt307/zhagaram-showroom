from pydantic import BaseModel
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    address: str
    email: Optional[str]
    phone: str


class CustomerUpdate(CustomerCreate):
    pass


class CustomerOut(CustomerCreate):
    id: int

    class Config:
        from_attributes = True
