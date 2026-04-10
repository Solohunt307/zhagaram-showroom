from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.expense import Expense

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from fastapi.responses import StreamingResponse


router = APIRouter(prefix="/accounting", tags=["Accounting"])


# ================================
# INVOICES LIST
# ================================

@router.get("/invoices")
def get_invoices(
    from_date: date | None = None,
    to_date: date | None = None,
    invoice_from: int | None = None,
    invoice_to: int | None = None,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    q = db.query(Sale).filter(Sale.showroom_id == showroom_id)

    if from_date:
        q = q.filter(Sale.sale_date >= from_date)

    if to_date:
        q = q.filter(Sale.sale_date <= to_date)

    if invoice_from:
        q = q.filter(Sale.invoice_no >= str(invoice_from))

    if invoice_to:
        q = q.filter(Sale.invoice_no <= str(invoice_to))

    total = q.count()

    rows = (
        q.order_by(Sale.sale_date.desc())
        .offset((page - 1) * 10)
        .limit(10)
        .all()
    )

    items = []

    for r in rows:
        items.append({
            "id": r.id,
            "invoice_no": r.invoice_number or r.id,
            "sale_date": r.sale_date,
            "order_amount": float(r.order_amount),
        })

    return {"items": items, "total": total}


# ================================
# ACCOUNTING SUMMARY
# ================================

@router.get("/summary")
def get_accounting_summary(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    # SALES
    sales_q = db.query(Sale).filter(Sale.showroom_id == showroom_id)

    if from_date:
        sales_q = sales_q.filter(Sale.sale_date >= from_date)

    if to_date:
        sales_q = sales_q.filter(Sale.sale_date <= to_date)

    # PURCHASE
    purchase_q = db.query(Purchase).filter(
        Purchase.showroom_id == showroom_id
    )

    if from_date:
        purchase_q = purchase_q.filter(Purchase.purchase_date >= from_date)

    if to_date:
        purchase_q = purchase_q.filter(Purchase.purchase_date <= to_date)

    # EXPENSE
    expense_q = db.query(Expense).filter(
        Expense.showroom_id == showroom_id
    )

    if from_date:
        expense_q = expense_q.filter(Expense.expense_date >= from_date)

    if to_date:
        expense_q = expense_q.filter(Expense.expense_date <= to_date)

    # CALCULATIONS

    total_sales = sales_q.with_entities(
        func.coalesce(func.sum(Sale.order_amount), 0)
    ).scalar()

    total_purchase = purchase_q.with_entities(
        func.coalesce(func.sum(Purchase.amount), 0)
    ).scalar()

    total_expense = expense_q.with_entities(
        func.coalesce(func.sum(Expense.amount), 0)
    ).scalar()

    sales_count = sales_q.count()
    purchase_count = purchase_q.count()

    net_profit = total_sales - total_purchase - total_expense

    return {
        "sales_count": sales_count,
        "purchase_count": purchase_count,
        "total_sales": float(total_sales),
        "total_purchase": float(total_purchase),
        "total_expense": float(total_expense),
        "net_profit": float(net_profit),
    }


# ================================
# EXPORT PDF
# ================================

@router.get("/export/pdf")
def export_invoices_pdf(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    q = db.query(Sale).filter(Sale.showroom_id == showroom_id)

    if from_date:
        q = q.filter(Sale.sale_date >= from_date)

    if to_date:
        q = q.filter(Sale.sale_date <= to_date)

    rows = q.order_by(Sale.sale_date.desc()).all()

    buffer = BytesIO()

    # ---------- PDF BUILD ----------
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    data = [["Invoice", "Date", "Amount"]]

    for r in rows:
        data.append([
            str(r.invoice_no or r.id),
            str(r.sale_date),
            f"₹ {r.order_amount}"
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    doc.build([
        Paragraph("Invoice Report", styles["Title"]),
        table
    ])

    # ---------- RESPONSE ----------
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=invoices.pdf"
        }
    )
