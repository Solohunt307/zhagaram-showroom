from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
import io

from app.core.database import get_db
from app.core.deps import get_current_user

from app.services.reports_service import *

router = APIRouter(prefix="/reports", tags=["Reports"])


# =====================================================
# COMMON PARAMS
# =====================================================

def common_params(
    from_date: date = Query(None),
    to_date: date = Query(None),
    page: int = Query(1),
    limit: int = Query(10),
    search: str = Query(None),
):
    return {
        "from_date": from_date,
        "to_date": to_date,
        "page": page,
        "limit": limit,
        "search": search
    }


# =====================================================
# KPI SUMMARY
# =====================================================

@router.get("/summary")
def summary(
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_kpi_summary(db, current_user["showroom_id"], params)


# =====================================================
# SALES TREND
# =====================================================

@router.get("/sales-trend")
def sales_trend(
    params: dict = Depends(common_params),
    group_by: str = Query("daily"),  # daily/monthly
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_sales_trend_advanced(
        db,
        showroom_id=current_user["showroom_id"],
        params=params,
        group_by=group_by
    )


# =====================================================
# TOP PRODUCTS
# =====================================================

@router.get("/top-products")
def top_products(
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_top_products_advanced(
        db,
        current_user["showroom_id"],
        params
    )


# =====================================================
# EMPLOYEE PERFORMANCE
# =====================================================

@router.get("/employee-performance")
def employee_performance(
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_employee_performance(
        db,
        current_user["showroom_id"],
        params
    )


# =====================================================
# SHOWROOM PERFORMANCE
# =====================================================

@router.get("/showroom-performance")
def showroom_performance(
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
):
    return get_showroom_performance(db, params)


# =====================================================
# CUSTOMER ANALYSIS
# =====================================================

@router.get("/customer-analysis")
def customer_analysis(
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_customer_analysis(
        db,
        current_user["showroom_id"],
        params
    )


# =====================================================
# PROFIT
# =====================================================

@router.get("/profit")
def profit(
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_profit_advanced(
        db,
        current_user["showroom_id"],
        params
    )


# =====================================================
# FORECAST
# =====================================================

@router.get("/forecast")
def forecast(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return forecast_demand(db, current_user["showroom_id"])


# =====================================================
# EXPORT
# =====================================================

@router.get("/export")
def export(
    type: str,
    params: dict = Depends(common_params),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):

    data, headers = get_export_data(
        db,
        current_user["showroom_id"],
        type,
        params
    )

    csv_data = export_reports_csv(data, headers)["csv"]

    buffer = io.StringIO(csv_data)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={type}.csv"
        }
    )
