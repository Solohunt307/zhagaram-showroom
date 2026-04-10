from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.models.service_ticket import ServiceTicket
from app.services.activity_service import log_activity


# ---------------- CREATE ----------------

def create_ticket(db, showroom_id, data, file_path, user_id):

    ticket = ServiceTicket(
        showroom_id=showroom_id,
        ticket_code=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        attachment_path=file_path,
        **data.dict()
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    log_activity(
        db,
        showroom_id,
        user_id,
        "SERVICE",
        f"Service ticket created {ticket.ticket_code}"
    )

    return ticket


# ---------------- LIST ----------------

def list_tickets(db, showroom_id, search=None, from_date=None, to_date=None, skip=0, limit=10):

    q = db.query(ServiceTicket).filter(ServiceTicket.showroom_id == showroom_id)

    if search:
        q = q.filter(
            or_(
                ServiceTicket.customer_name.ilike(f"%{search}%"),
                ServiceTicket.product_name.ilike(f"%{search}%"),
                ServiceTicket.ticket_code.ilike(f"%{search}%"),
            )
        )

    if from_date:
        q = q.filter(ServiceTicket.created_at >= from_date)

    if to_date:
        q = q.filter(ServiceTicket.created_at <= to_date)

    total = q.count()

    items = (
        q.order_by(ServiceTicket.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


# ---------------- UPDATE ----------------

def update_ticket(db, ticket, data, file_path, user_id):

    for k, v in data.dict().items():
        setattr(ticket, k, v)

    if file_path:
        ticket.attachment_path = file_path

    db.commit()

    log_activity(
        db,
        ticket.showroom_id,
        user_id,
        "SERVICE",
        f"Ticket updated {ticket.ticket_code}"
    )

    return ticket


# ---------------- DELETE ----------------

def delete_ticket(db, ticket, user_id):

    db.delete(ticket)
    db.commit()

    log_activity(
        db,
        ticket.showroom_id,
        user_id,
        "SERVICE",
        f"Ticket deleted {ticket.ticket_code}"
    )


# ---------------- CSV EXPORT ----------------

def export_tickets_csv(db, showroom_id):

    rows = (
        db.query(ServiceTicket)
        .filter(ServiceTicket.showroom_id == showroom_id)
        .all()
    )

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "Ticket",
        "Customer",
        "Product",
        "Complaint",
        "Technician",
        "Status",
        "Created",
        "Closed",
        "Cost",
        "Paid",
        "Balance"
    ])

    for t in rows:
        writer.writerow([
            t.ticket_code,
            t.customer_name,
            t.product_name,
            t.complaint,
            t.technician,
            t.status,
            t.created_at,
            t.closed_at,
            t.service_cost,
            t.amount_paid,
            t.balance,
        ])

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=service_tickets.csv"}
    )

# =============================
# CLOSE TICKET
# =============================

def close_ticket(db, ticket, user_id):

    ticket.status = "CLOSED"

    db.commit()
    db.refresh(ticket)

    from app.services.activity_service import log_activity

    log_activity(
        db,
        ticket.showroom_id,
        user_id,
        "SERVICE",
        f"Ticket closed: {ticket.ticket_code}"
    )

    return ticket
