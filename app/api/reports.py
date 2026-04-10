from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.reports_service import (
    sales_summary,
    top_products,
    showroom_sales,
    sales_rep_performance,
    profit_report,
    repeat_customers,
    demand_forecast,
)

router = APIRouter(prefix="/reports", tags=["Reports & Analysis"])


@router.get("/sales-summary")
def get_sales_summary(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sales_summary(db, current_user["showroom_id"], start, end)


@router.get("/top-products")
def get_top_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return top_products(db, current_user["showroom_id"])


@router.get("/showroom-sales")
def get_showroom_sales(db: Session = Depends(get_db)):
    return showroom_sales(db)


@router.get("/sales-rep")
def get_sales_rep(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return sales_rep_performance(db, current_user["showroom_id"])


@router.get("/profit")
def get_profit(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return {"profit": profit_report(db, current_user["showroom_id"])}


@router.get("/repeat-customers")
def get_repeat_customers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return repeat_customers(db, current_user["showroom_id"])


@router.get("/forecast")
def get_forecast(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return demand_forecast(db, current_user["showroom_id"])
