from pydantic import BaseModel
from typing import Optional
from datetime import date


class VendorCreate(BaseModel):
    name: str
    mobile: str
    email: Optional[str]
    gst_no: Optional[str]
    location: str


class VendorOut(VendorCreate):
    id: int

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    product_id: int
    vendor_id: int
    quantity: int
    color: Optional[str]
    amount: float
    payment_mode: str
    shipment_mode: Optional[str]
    notes: Optional[str]
    purchase_date: date


class PurchaseOut(PurchaseCreate):
    id: int
    product_name: str
    vendor_name: str

    class Config:
        from_attributes = True
