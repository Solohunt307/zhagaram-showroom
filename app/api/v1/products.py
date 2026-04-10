from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut
from app.models.product import Product
from app.services.product_service import (
    create_product,
    list_products,
    update_product,
    delete_product
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductOut)
def add_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_product(
        db,
        current_user["showroom_id"],
        data,
        current_user["sub"]
    )


@router.get("/")
def get_products(
    search: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    skip = (page - 1) * 10

    query = db.query(Product).filter(
        Product.showroom_id == current_user["showroom_id"],Product.is_active == True
    )

    if search:
        query = query.filter(
            or_(
                Product.product_name.ilike(f"%{search}%"),
                Product.model.ilike(f"%{search}%"),
                Product.variant.ilike(f"%{search}%")
            )
        )

    if from_date:
        query = query.filter(
            Product.created_at >= datetime.fromisoformat(from_date)
        )

    if to_date:
        query = query.filter(
            Product.created_at <= datetime.fromisoformat(to_date)
        )

    total = query.count()

    items = query.offset(skip).limit(10).all()

    return {
        "items": items,
        "total": total,
        "page": page
    }


@router.put("/{product_id}", response_model=ProductOut)
def edit_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.showroom_id == current_user["showroom_id"]
        )
        .first()
    )

    if not product:
        raise HTTPException(404, "Product not found")

    return update_product(db, product, data, current_user["sub"])


@router.delete("/{product_id}")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.showroom_id == current_user["showroom_id"]
        )
        .first()
    )

    if not product:
        raise HTTPException(404, "Product not found")

    delete_product(db, product, current_user["sub"])

    return {"message": "Deleted"}
