from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import uuid, os, shutil
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user

from app.schemas.service_ticket import ServiceTicketCreate
from app.services.service_ticket_service import (
    create_ticket,
    list_tickets,
    update_ticket,
    delete_ticket,
    export_tickets_csv,
)

from app.models.service_ticket import ServiceTicket

UPLOAD_DIR = "uploads/service"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/service", tags=["Service"])


# ================= CREATE =================

@router.post("/")
def create_service_ticket(

    customer_name: str | None = Form(None),
    product_name: str | None = Form(None),
    product_description: str | None = Form(None),
    complaint: str | None = Form(None),
    mobile: str | None = Form(None),
    technician: str | None = Form(None),
    status: str | None = Form("OPEN"),

    resolved_complaint: str | None = Form(None),
    unresolved_complaint: str | None = Form(None),

    bill_no: str | None = Form(None),
    received_by: str | None = Form(None),
    service_completed_date: date | None = Form(None),

    service_cost: float | None = Form(None),
    amount_paid: float | None = Form(None),
    balance: float | None = Form(None),

    payment_mode: str | None = Form(None),
    payment_date: date | None = Form(None),

    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    file_path = None

    if file and file.filename:
        ext = Path(file.filename).suffix
        safe = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    data = ServiceTicketCreate(
        customer_name=customer_name,
        product_name=product_name,
        product_description=product_description,
        complaint=complaint,
        mobile=mobile,
        technician=technician,
        status=status,
        resolved_complaint=resolved_complaint,
        unresolved_complaint=unresolved_complaint,
        bill_no=bill_no,
        received_by=received_by,
        service_completed_date=service_completed_date,
        service_cost=service_cost,
        amount_paid=amount_paid,
        balance=balance,
        payment_mode=payment_mode,
        payment_date=payment_date,
    )

    return create_ticket(
        db,
        current_user["showroom_id"],
        data,
        file_path,
        current_user["sub"],
    )


# ================= LIST =================

@router.get("/")
def get_tickets(
    search: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_tickets(
        db,
        current_user["showroom_id"],
        search,
        from_date,
        to_date,
        skip,
    )

    return {"items": items, "total": total}


# ================= GET SINGLE =================

@router.get("/{ticket_id}")
def get_single_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    ticket = (
        db.query(ServiceTicket)
        .filter(
            ServiceTicket.id == ticket_id,
            ServiceTicket.showroom_id == current_user["showroom_id"]
        )
        .first()
    )

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    return ticket


# ================= UPDATE (FIXED) =================

@router.put("/{ticket_id}")
def edit_ticket(

    ticket_id: int,

    customer_name: str | None = Form(None),
    product_name: str | None = Form(None),
    product_description: str | None = Form(None),
    complaint: str | None = Form(None),
    mobile: str | None = Form(None),
    technician: str | None = Form(None),
    status: str | None = Form(None),

    resolved_complaint: str | None = Form(None),
    unresolved_complaint: str | None = Form(None),

    bill_no: str | None = Form(None),
    received_by: str | None = Form(None),
    service_completed_date: date | None = Form(None),

    service_cost: float | None = Form(None),
    amount_paid: float | None = Form(None),
    balance: float | None = Form(None),

    payment_mode: str | None = Form(None),
    payment_date: date | None = Form(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    ticket = (
        db.query(ServiceTicket)
        .filter(
            ServiceTicket.id == ticket_id,
            ServiceTicket.showroom_id == current_user["showroom_id"]
        )
        .first()
    )

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    data = ServiceTicketCreate(
        customer_name=customer_name,
        product_name=product_name,
        product_description=product_description,
        complaint=complaint,
        mobile=mobile,
        technician=technician,
        status=status,
        resolved_complaint=resolved_complaint,
        unresolved_complaint=unresolved_complaint,
        bill_no=bill_no,
        received_by=received_by,
        service_completed_date=service_completed_date,
        service_cost=service_cost,
        amount_paid=amount_paid,
        balance=balance,
        payment_mode=payment_mode,
        payment_date=payment_date,
    )

    return update_ticket(
        db,
        ticket,
        data,
        None,
        current_user["sub"]
    )


# ================= DELETE =================

@router.delete("/{ticket_id}")
def remove_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    ticket = (
        db.query(ServiceTicket)
        .filter(
            ServiceTicket.id == ticket_id,
            ServiceTicket.showroom_id == current_user["showroom_id"]
        )
        .first()
    )

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    delete_ticket(db, ticket, current_user["sub"])

    return {"message": "Deleted"}


# ================= CSV =================

@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return export_tickets_csv(db, current_user["showroom_id"])