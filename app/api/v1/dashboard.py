from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user

from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.expense import Expense
from app.models.service_ticket import ServiceTicket

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# =====================================
# KPI SUMMARY
# =====================================

@router.get("/kpis")
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    showroom_id = current_user["showroom_id"]

# 🚨 HANDLE NULL SHOWROOM (ADMIN BEFORE SELECTION)
    if not showroom_id:
        return {
	        "total_sales": 0,
        	"total_purchase": 0,
        	"total_expenses": 0,
        	"gross_profit": 0,
        	"net_profit": 0,
        	"active_tickets": 0,
        	"closed_tickets": 0,
    	    }

    # ---------------- SALES ----------------

    total_sales = (
        db.query(func.coalesce(func.sum(Sale.order_amount), 0))
        .filter(Sale.showroom_id == showroom_id)
        .scalar()
    )

    # ---------------- PURCHASE ----------------

    total_purchase = (
        db.query(func.coalesce(func.sum(Purchase.amount), 0))
        .filter(Purchase.showroom_id == showroom_id)
        .scalar()
    )

    # ---------------- EXPENSES ----------------

    total_expenses = (
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.showroom_id == showroom_id)
        .scalar()
    )

    # ---------------- PROFITS ----------------

    gross_profit = total_sales - total_purchase

    net_profit = total_sales - total_purchase - total_expenses

    # ---------------- SERVICE TICKETS ----------------

    active_tickets = (
        db.query(func.count(ServiceTicket.id))
        .filter(
            ServiceTicket.showroom_id == showroom_id,
            func.coalesce(ServiceTicket.status, "OPEN") != "Resolved"
        )
        .scalar()
    )

    closed_tickets = (
        db.query(func.count(ServiceTicket.id))
        .filter(
            ServiceTicket.showroom_id == showroom_id,
            ServiceTicket.status == "Resolved"
        )
        .scalar()
    )

    return {
        "total_sales": round(total_sales, 2),
        "total_purchase": round(total_purchase, 2),
        "total_expenses": round(total_expenses, 2),
        "gross_profit": round(gross_profit, 2),
        "net_profit": round(net_profit, 2),
        "active_tickets": active_tickets,
        "closed_tickets": closed_tickets,
    }


# =====================================
# DAILY SALES CHART
# =====================================

@router.get("/daily-sales")
def daily_sales_chart(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    showroom_id = current_user["showroom_id"]

    start_date = date.today() - timedelta(days=days)

    rows = (
        db.query(
            Sale.sale_date,
            func.sum(Sale.order_amount).label("total")
        )
        .filter(
            Sale.showroom_id == showroom_id,
            Sale.sale_date >= start_date,
        )
        .group_by(Sale.sale_date)
        .order_by(Sale.sale_date)
        .all()
    )

    labels = []
    values = []

    for r in rows:
        labels.append(r.sale_date.strftime("%d %b"))
        values.append(float(r.total))

    return {
        "labels": labels,
        "values": values,
    }
