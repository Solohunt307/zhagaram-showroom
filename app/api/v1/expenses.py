from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user

from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseBulkCreate,
    ExpenseOut,
)

from app.services.expense_service import (
    create_expense,
    bulk_create_expenses,
    list_expenses,
    update_expense,
    delete_expense,
    export_expense_csv,
)

from app.models.expense import Expense

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# =============================
# CREATE
# =============================

@router.post("/", response_model=ExpenseOut)
def add_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return create_expense(
        db,
        current_user["showroom_id"],
        data,
        current_user["sub"],
    )


# =============================
# BULK DAILY
# =============================

@router.post("/bulk")
def bulk_add(
    data: ExpenseBulkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    bulk_create_expenses(
        db,
        current_user["showroom_id"],
        data.items,
        current_user["sub"],
    )

    return {"message": "Expenses added"}


# =============================
# LIST
# =============================

@router.get("/")
def get_expenses(
    search: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_expenses(
        db,
        current_user["showroom_id"],
        search,
        from_date,
        to_date,
        skip,
    )

    return {"items": items, "total": total}


# =============================
# UPDATE
# =============================

@router.put("/{exp_id}", response_model=ExpenseOut)
def edit_expense(
    exp_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    exp = (
        db.query(Expense)
        .filter(
            Expense.id == exp_id,
            Expense.showroom_id ==
            current_user["showroom_id"]
        )
        .first()
    )

    if not exp:
        raise HTTPException(404, "Expense not found")

    return update_expense(db, exp, data, current_user["sub"])


# =============================
# DELETE
# =============================

@router.delete("/{exp_id}")
def remove_expense(
    exp_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    exp = (
        db.query(Expense)
        .filter(
            Expense.id == exp_id,
            Expense.showroom_id ==
            current_user["showroom_id"]
        )
        .first()
    )

    if not exp:
        raise HTTPException(404, "Expense not found")

    delete_expense(db, exp, current_user["sub"])

    return {"message": "Deleted"}


# =============================
# EXPORT CSV
# =============================

@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return export_expense_csv(
        db,
        current_user["showroom_id"]
    )
