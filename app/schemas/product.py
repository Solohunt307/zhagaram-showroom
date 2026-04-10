from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    product_name: str
    hsn: str
    model: str
    variant: str
    color: str
    purchase_price: float | None = None
    sale_price: float
    tax_rate: float | None = None
    stock_qty: int = 0
    low_stock_threshold: int = 0
    description: str | None = None


class ProductUpdate(ProductCreate):
    pass


class ProductOut(ProductCreate):
    id: int

    class Config:
        from_attributes = True
