from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import decode_access_token

from app.models.sale import Sale

from app.services.sale_service import (
    create_sale,
    list_sales,
    get_sale_by_id,
    delete_sale,
    add_payment_to_sale,
    export_sales_csv_file,
    cancel_sale_and_restore_stock,
    generate_invoice_pdf,
    get_daily_sales_dashboard,
    get_range_sales_dashboard,
)

router = APIRouter(prefix="/sales", tags=["Sales"])



# =====================================================
# CREATE SALE
# =====================================================

@router.post("/")
def create_sale_api(
    customer_name: str = Form(...),
    phone: str = Form(...),
    address: str | None = Form(None),

    product_id: int = Form(...),
    quantity: int = Form(...),

    order_amount: float = Form(...),
    paid_amount: float = Form(...),

    payment_type: str = Form(...),
    sale_date: date = Form(...),

    received_by: str = Form(...),
    notes: str | None = Form(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return create_sale(
        db=db,
        showroom_id=current_user["showroom_id"],
        customer_name=customer_name,
        phone=phone,
        address=address,
        product_id=product_id,
        quantity=quantity,
        order_amount=order_amount,
        paid_amount=paid_amount,
        payment_type=payment_type,
        sale_date=sale_date,
        received_by=received_by,
        notes=notes,
        created_by=current_user["sub"],
    )



@router.put("/{sale_id}")
def update_sale_api(
    sale_id: int,
    customer_name: str = Form(...),
    phone: str = Form(...),
    address: str | None = Form(None),

    product_id: int = Form(...),
    quantity: int = Form(...),

    order_amount: float = Form(...),
    paid_amount: float = Form(...),

    payment_type: str = Form(...),
    sale_date: date = Form(...),

    received_by: str = Form(...),
    notes: str | None = Form(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    sale = db.get(Sale, sale_id)

    if not sale:
        raise HTTPException(404, "Sale not found")

    if sale.showroom_id != current_user["showroom_id"]:
        raise HTTPException(403, "Unauthorized")

    # simple update (no stock change for now)
    sale.quantity = quantity
    sale.order_amount = order_amount
    sale.paid_amount = paid_amount
    sale.balance_amount = order_amount - paid_amount
    sale.payment_type = payment_type
    sale.sale_date = sale_date
    sale.received_by = received_by
    sale.notes = notes

    db.commit()
    db.refresh(sale)

    return {"success": True}


# =====================================================
# LIST SALES
# =====================================================

@router.get("/")
def list_sales_api(
    page: int = 1,
    search: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_sales(
        db,
        showroom_id=current_user["showroom_id"],
        search=search,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
    )

    return {"items": items, "total": total}



# =====================================================
# GET SINGLE SALE
# =====================================================

@router.get("/{sale_id}")
def get_sale_detail(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return get_sale_by_id(
        db,
        sale_id,
        current_user["showroom_id"],
    )



# =====================================================
# DELETE SALE
# =====================================================

@router.delete("/{sale_id}")
def delete_sale_api(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    delete_sale(
        db,
        sale_id,
        current_user["showroom_id"],
    )

    return {"success": True}


#----------------------------------------------------------


@router.post("/{sale_id}/payments")
def add_sale_payment(
    sale_id: int,
    amount: float = Form(...),
    payment_type: str = Form(...),
    received_by: str = Form(...),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    sale = db.get(Sale, sale_id)

    if not sale:
        raise HTTPException(404, "Sale not found")

    if amount <= 0:
        raise HTTPException(400, "Invalid amount")

    if sale.balance_amount <= 0:
        raise HTTPException(400, "No balance remaining")

    if amount > sale.balance_amount:
        raise HTTPException(400, "Payment exceeds balance")

    return add_payment_to_sale(
        db,
        sale,
        amount,
        payment_type,
        received_by,
        current_user["sub"]
    )





@router.post("/{sale_id}/cancel")
def cancel_sale_api(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    sale = db.get(Sale, sale_id)

    if not sale:
        raise HTTPException(404, "Sale not found")

    if sale.status == "CANCELLED":
        raise HTTPException(400, "Already cancelled")

    return cancel_sale_and_restore_stock(
        db,
        sale,
        current_user["sub"]
    )


@router.get("/{sale_id}/invoice")
def download_invoice_pdf(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    sale = (
        db.query(Sale)
        .filter(
            Sale.id == sale_id,
            Sale.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not sale:
        raise HTTPException(404, "Sale not found")

    buffer, filename = generate_invoice_pdf(db, sale)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={filename}"
        }
    )

@router.get("/dashboard/daily")
def daily_dashboard(
    date_: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return get_daily_sales_dashboard(
        db,
        current_user["showroom_id"],
        date_,
    )


@router.get("/dashboard/range")
def range_dashboard(
    from_date: date,
    to_date: date,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return get_range_sales_dashboard(
        db,
        current_user["showroom_id"],
        from_date,
        to_date,
    )


@router.get("/export/csv")
def export_sales_csv(
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(401, "Invalid token")

    showroom_id = payload.get("showroom_id")

    return export_sales_csv_file(db, showroom_id)