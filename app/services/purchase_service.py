from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models.vendor import Vendor
from app.models.purchase import Purchase
from app.models.product import Product
from app.services.activity_service import log_activity


# ---------------- Vendors ----------------

def create_vendor(db: Session, showroom_id: int, data, user_id: int):

    vendor = Vendor(**data.dict(), showroom_id=showroom_id)

    db.add(vendor)
    db.commit()
    db.refresh(vendor)

    log_activity(db, showroom_id, user_id, "PURCHASES", f"Vendor added: {vendor.name}")

    return vendor


def list_vendors(db: Session, showroom_id: int, search=None, skip=0, limit=10):

    q = db.query(Vendor).filter(Vendor.showroom_id == showroom_id, Vendor.is_active == True)

    if search:
        q = q.filter(Vendor.name.ilike(f"%{search}%"))

    return q.offset(skip).limit(limit).all(), q.count()


def update_vendor(db: Session, vendor: Vendor, data, user_id: int):

    for k, v in data.dict().items():
        setattr(vendor, k, v)

    db.commit()

    log_activity(db, vendor.showroom_id, user_id, "PURCHASES", f"Vendor updated: {vendor.name}")

    return vendor


def delete_vendor(db: Session, vendor: Vendor, user_id: int):

    vendor.is_active = False   # ✅ soft delete

    db.commit()

    log_activity(
        db,
        vendor.showroom_id,
        user_id,
        "PURCHASES",
        f"Vendor deactivated: {vendor.name}"
    )


# ---------------- Purchases ----------------

def create_purchase(db, showroom_id, data, file_path, user_id):

    purchase = Purchase(
        **data.dict(),
        showroom_id=showroom_id,
        file_path=file_path
    )

    db.add(purchase)

    # 🔥 AUTO UPDATE STOCK
    product = db.get(Product, data.dict()["product_id"])

    if product:
        product.stock_qty += data.dict()["quantity"]

    db.commit()
    db.refresh(purchase)

    log_activity(
        db,
        showroom_id,
        user_id,
        "PURCHASES",
        f"Purchase added for product ID {purchase.product_id}"
    )

    return purchase


def list_purchases(db, showroom_id, search, from_date, to_date, skip, limit=10):

    q = (
        db.query(Purchase)
        .options(
            joinedload(Purchase.product),
            joinedload(Purchase.vendor),
        )
        .filter(Purchase.showroom_id == showroom_id)
    )

    if from_date:
        q = q.filter(Purchase.purchase_date >= from_date)

    if to_date:
        q = q.filter(Purchase.purchase_date <= to_date)

    if search:
        q = q.join(Purchase.vendor).join(Purchase.product).filter(
                   or_(
                       Vendor.name.ilike(f"%{search}%"),
                       Product.product_name.ilike(f"%{search}%")
        )
    )

    total = q.count()

    return q.offset(skip).limit(limit).all(), total


def update_purchase(db, purchase, data, file_path, user_id):

    old_qty = purchase.quantity
    new_qty = data.dict()["quantity"]

    diff = new_qty - old_qty

    product = db.get(Product, purchase.product_id)

    if product:
        product.stock_qty += diff

    for k, v in data.dict().items():
        setattr(purchase, k, v)

    if file_path:
        purchase.file_path = file_path

    db.commit()
    db.refresh(purchase)

    return purchase



def delete_purchase(db: Session, purchase: Purchase, user_id: int):

    db.delete(purchase)
    db.commit()

    log_activity(
        db,
        purchase.showroom_id,
        user_id,
        "PURCHASES",
        f"Purchase deleted #{purchase.id}",
    )
