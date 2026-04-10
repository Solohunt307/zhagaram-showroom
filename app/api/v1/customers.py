from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.responses import StreamingResponse
import io, csv

from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
)
from app.models.customer import Customer
from app.services.customer_service import (
    create_customer,
    list_customers,
    update_customer,
    delete_customer,
    export_customers_csv,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerOut)
def add_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_customer(
        db,
        current_user["showroom_id"],
        data,
        current_user["sub"]
    )


@router.get("/")
def get_customers(
    search: str | None = None,
    page: int = 1,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    skip = (page - 1) * 10

    items, total = list_customers(
        db,
        current_user["showroom_id"],
        search,
        skip,
        from_date,
        to_date,
    )

    return {"items": items, "total": total}


@router.put("/{customer_id}", response_model=CustomerOut)
def edit_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not customer:
        raise HTTPException(404, "Customer not found")

    return update_customer(db, customer, data, current_user["sub"])


@router.delete("/{customer_id}")
def remove_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not customer:
        raise HTTPException(404, "Customer not found")

    delete_customer(db, customer, current_user["sub"])

    return {"message": "Deleted"}

@router.get("/export/csv")
def export_customers_csv_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    return export_customers_csv(db, showroom_id)




@router.get("/export/csv")
def export_customers_csv_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    csv_data = export_customers_csv(db, showroom_id)

    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=customers.csv"
        },
    )
