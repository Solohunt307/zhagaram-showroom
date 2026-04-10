from sqlalchemy.orm import Session
from sqlalchemy import or_

import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.models.expense import Expense
from app.services.activity_service import log_activity


# =============================
# CREATE SINGLE
# =============================

def create_expense(db: Session, showroom_id, data, user_id):

    exp = Expense(
        showroom_id=showroom_id,
        created_by=user_id,
        **data.dict()
    )

    db.add(exp)
    db.commit()
    db.refresh(exp)

    log_activity(
        db,
        showroom_id,
        user_id,
        "EXPENSE",
        f"Expense added: {data.category} ₹{data.amount}"
    )

    return exp


# =============================
# BULK CREATE
# =============================

def bulk_create_expenses(db, showroom_id, items, user_id):

    rows = []

    for data in items:

        rows.append(
            Expense(
                showroom_id=showroom_id,
                created_by=user_id,
                **data.dict()
            )
        )

    db.add_all(rows)
    db.commit()

    log_activity(
        db,
        showroom_id,
        user_id,
        "EXPENSE",
        f"{len(items)} expenses added"
    )

    return rows


# =============================
# LIST
# =============================

def list_expenses(
    db,
    showroom_id,
    search=None,
    from_date=None,
    to_date=None,
    skip=0,
    limit=10,
):

    q = db.query(Expense).filter(
        Expense.showroom_id == showroom_id
    )

    if search:
        q = q.filter(
            or_(
                Expense.description.ilike(f"%{search}%"),
                Expense.category.ilike(f"%{search}%"),
            )
        )

    if from_date:
        q = q.filter(Expense.expense_date >= from_date)

    if to_date:
        q = q.filter(Expense.expense_date <= to_date)

    total = q.count()

    items = (
        q.order_by(Expense.expense_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items, total


# =============================
# UPDATE
# =============================

def update_expense(db, exp, data, user_id):

    for k, v in data.dict().items():
        setattr(exp, k, v)

    db.commit()

    log_activity(
        db,
        exp.showroom_id,
        user_id,
        "EXPENSE",
        f"Expense updated ID {exp.id}"
    )

    return exp


# =============================
# DELETE
# =============================

def delete_expense(db, exp, user_id):

    db.delete(exp)
    db.commit()

    log_activity(
        db,
        exp.showroom_id,
        user_id,
        "EXPENSE",
        f"Expense deleted ID {exp.id}"
    )


# =============================
# EXPORT CSV
# =============================

def export_expense_csv(db, showroom_id):

    rows = (
        db.query(Expense)
        .filter(Expense.showroom_id == showroom_id)
        .order_by(Expense.expense_date.desc())
        .all()
    )

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "Category",
        "Description",
        "Amount",
        "Expense Date",
        "Created By"
    ])

    for r in rows:
        writer.writerow([
            r.category,
            r.description,
            r.amount,
            r.expense_date,
            r.created_by,
        ])

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=expenses.csv"
        }
    )
