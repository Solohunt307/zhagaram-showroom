from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
import csv, io

from app.models.customer import Customer
from app.services.activity_service import log_activity


# ======================================================
# CREATE CUSTOMER
# ======================================================

def create_customer(db: Session, showroom_id: int, data, user_id: int):

    customer = Customer(
        showroom_id=showroom_id,
        **data.dict()
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    log_activity(
        db,
        showroom_id,
        user_id,
        "CUSTOMERS",
        f"Customer added: {customer.name}"
    )

    return customer


# ======================================================
# LIST CUSTOMERS
# ======================================================

def list_customers(
    db: Session,
    showroom_id: int,
    search=None,
    skip=0,
    limit=10,
    from_date: date | None = None,
    to_date: date | None = None,
):

    # ✅ FIX: separate filters (important)
    q = (
        db.query(Customer)
        .filter(Customer.showroom_id == showroom_id)
        .filter(Customer.is_active == True)
    )

    if search:
        q = q.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
            )
        )

    if from_date:
        q = q.filter(Customer.created_at >= from_date)

    if to_date:
        q = q.filter(Customer.created_at <= to_date)

    total = q.count()

    rows = (
        q.order_by(Customer.name)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return rows, total


# ======================================================
# UPDATE CUSTOMER
# ======================================================

def update_customer(db: Session, customer, data, user_id):

    for k, v in data.dict().items():
        setattr(customer, k, v)

    db.commit()

    log_activity(
        db,
        customer.showroom_id,
        user_id,
        "CUSTOMERS",
        f"Customer updated: {customer.name}"
    )

    return customer


# ======================================================
# DELETE CUSTOMER (SOFT DELETE)
# ======================================================

def delete_customer(db: Session, customer, user_id):

    customer.is_active = False   # ✅ soft delete

    db.commit()

    log_activity(
        db,
        customer.showroom_id,
        user_id,
        "CUSTOMERS",
        f"Customer deactivated: {customer.name}"
    )


# ======================================================
# EXPORT CSV
# ======================================================

def export_customers_csv(db: Session, showroom_id: int):

    output = io.StringIO()

    # ✅ IMPORTANT: ensure proper CSV formatting
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    writer.writerow([
        "Name",
        "Address",
        "Email",
        "Phone",
        "Created At",
    ])

    rows = (
        db.query(Customer)
        .filter(Customer.showroom_id == showroom_id)
        .filter(Customer.is_active == True)   # ✅ important
        .order_by(Customer.name)
        .all()
    )

    for c in rows:
        writer.writerow([
            c.name,
            c.address,
            c.email or "",   # ✅ avoid None
            c.phone,
            c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else ""
        ])

    return '\ufeff' + output.getvalue()