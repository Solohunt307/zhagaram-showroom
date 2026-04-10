from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import shutil, os

from app.core.database import get_db
from app.core.deps import get_current_user

from app.schemas.purchase import VendorCreate, VendorOut
from app.services.purchase_service import *

from app.models.vendor import Vendor
from app.models.purchase import Purchase

# ======================================================
# FILE UPLOAD PATH
# ======================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "purchases")

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ======================================================

router = APIRouter(prefix="/purchases", tags=["Purchases"])

# ======================================================
# ---------------- VENDORS -----------------------------
# ======================================================

@router.post("/vendors", response_model=VendorOut)
def add_vendor(
    data: VendorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_vendor(
        db,
        current_user["showroom_id"],
        data,
        current_user["sub"],
    )


@router.get("/vendors")
def get_vendors(
    page: int = 1,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_vendors(
        db,
        current_user["showroom_id"],
        search,
        skip,
    )

    return {"items": items, "total": total}


@router.put("/vendors/{vendor_id}")
def edit_vendor(
    vendor_id: int,
    data: VendorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    vendor = db.get(Vendor, vendor_id)

    if not vendor:
        raise HTTPException(404, "Vendor not found")

    return update_vendor(
        db,
        vendor,
        data,
        current_user["sub"],
    )


@router.delete("/vendors/{vendor_id}")
def remove_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    vendor = db.get(Vendor, vendor_id)

    if not vendor:
        raise HTTPException(404, "Vendor not found")

    delete_vendor(db, vendor, current_user["sub"])

    return {"success": True}

# ======================================================
# ---------------- PURCHASES ---------------------------
# ======================================================

@router.post("/")
def add_purchase(
    product_id: int = Form(...),
    vendor_id: int = Form(...),
    quantity: int = Form(...),
    color: str | None = Form(None),
    amount: float = Form(...),
    payment_mode: str = Form(...),
    shipment_mode: str | None = Form(None),
    notes: str | None = Form(None),
    purchase_date: date = Form(...),
    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    file_path = None

    if file and file.filename:
        safe_name = os.path.basename(file.filename)

        path = os.path.join(UPLOAD_DIR, safe_name)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_path = path

    data = {
        "product_id": product_id,
        "vendor_id": vendor_id,
        "quantity": quantity,
        "color": color,
        "amount": amount,
        "payment_mode": payment_mode,
        "shipment_mode": shipment_mode,
        "notes": notes,
        "purchase_date": purchase_date,
    }

    return create_purchase(
        db,
        current_user["showroom_id"],
        type("obj", (), {"dict": lambda self=data: data})(),
        file_path,
        current_user["sub"],
    )


@router.get("/")
def get_purchases(
    page: int = 1,
    search: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_purchases(
        db,
        current_user["showroom_id"],
        search,
        from_date,
        to_date,
        skip,
    )

    result = []

    for p in items:
        result.append({
            "id": p.id,
            "product_id": p.product_id,
            "vendor_id": p.vendor_id,

            "product_name": p.product.product_name,
            "vendor_name": p.vendor.name,

            "quantity": p.quantity,
            "amount": p.amount,
            "payment_mode": p.payment_mode,
            "shipment_mode": p.shipment_mode,
            "notes": p.notes,

            "purchase_date": p.purchase_date,
        })

    return {"items": result, "total": total}



@router.put("/{purchase_id}")
def edit_purchase(
    purchase_id: int,

    product_id: int = Form(...),
    vendor_id: int = Form(...),
    quantity: int = Form(...),
    color: str | None = Form(None),
    amount: float = Form(...),
    payment_mode: str = Form(...),
    shipment_mode: str | None = Form(None),
    notes: str | None = Form(None),
    purchase_date: date = Form(...),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    purchase = db.get(Purchase, purchase_id)

    if not purchase:
        raise HTTPException(404, "Purchase not found")

    data = {
        "product_id": product_id,
        "vendor_id": vendor_id,
        "quantity": quantity,
        "color": color,
        "amount": amount,
        "payment_mode": payment_mode,
        "shipment_mode": shipment_mode,
        "notes": notes,
        "purchase_date": purchase_date,
    }

    return update_purchase(
        db,
        purchase,
        type("obj", (), {"dict": lambda self=data: data})(),
        None,
        current_user["sub"],
    )


@router.delete("/{purchase_id}")
def remove_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    purchase = db.get(Purchase, purchase_id)

    if not purchase:
        raise HTTPException(404, "Purchase not found")

    delete_purchase(db, purchase, current_user["sub"])

    return {"success": True}
