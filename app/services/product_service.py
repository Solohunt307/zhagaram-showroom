from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product
from app.services.activity_service import log_activity


def create_product(db: Session, showroom_id: int, data, user_id: int):
    product = Product(**data.dict(), showroom_id=showroom_id)

    db.add(product)
    db.commit()
    db.refresh(product)

    log_activity(
        db,
        showroom_id,
        user_id,
        "INVENTORY",
        f"Product added: {product.product_name}"
    )

    return product


def list_products(db: Session, showroom_id: int, search=None, skip=0, limit=10):
    query = db.query(Product).filter(Product.showroom_id == showroom_id,Product.is_active == True)

    if search:
        query = query.filter(
            or_(
                Product.product_name.ilike(f"%{search}%"),
                Product.model.ilike(f"%{search}%"),
                Product.variant.ilike(f"%{search}%")
            )
        )

    return query.offset(skip).limit(limit).all(), query.count()


def update_product(db: Session, product: Product, data, user_id: int):
    for field, value in data.dict().items():
        setattr(product, field, value)

    db.commit()

    log_activity(
        db,
        product.showroom_id,
        user_id,
        "INVENTORY",
        f"Product updated: {product.product_name}"
    )

    return product


def delete_product(db: Session, product: Product, user_id: int):

    product.is_active = False   # ✅ soft delete

    db.commit()

    log_activity(
        db,
        product.showroom_id,
        user_id,
        "INVENTORY",
        f"Product deactivated: {product.product_name}"
    )
