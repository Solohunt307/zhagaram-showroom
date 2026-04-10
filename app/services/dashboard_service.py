from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.vehicle import Vehicle
from app.models.sale import Sale
from app.models.enquiry import Enquiry
from app.models.activity_log import ActivityLog


def get_dashboard_kpis(db: Session, showroom_id: int):
    total_stock = db.query(func.sum(Vehicle.stock_qty))\
        .filter(Vehicle.showroom_id == showroom_id).scalar() or 0

    low_stock = db.query(Vehicle)\
        .filter(
            Vehicle.showroom_id == showroom_id,
            Vehicle.stock_qty <= Vehicle.low_stock_threshold
        ).count()

    current_month = datetime.utcnow().month

    vehicles_sold = db.query(Sale)\
        .filter(
            Sale.showroom_id == showroom_id,
            func.extract('month', Sale.sold_at) == current_month
        ).count()

    total_sales = db.query(func.sum(Sale.sale_amount))\
        .filter(
            Sale.showroom_id == showroom_id,
            func.extract('month', Sale.sold_at) == current_month
        ).scalar() or 0

    active_enquiries = db.query(Enquiry)\
        .filter(
            Enquiry.showroom_id == showroom_id,
            Enquiry.is_active == True
        ).count()

    today_activities = db.query(ActivityLog)\
        .filter(
            ActivityLog.showroom_id == showroom_id,
            func.date(ActivityLog.created_at) == datetime.utcnow().date()
        ).count()

    return {
        "total_stock": total_stock,
        "low_stock_alerts": low_stock,
        "vehicles_sold_this_month": vehicles_sold,
        "total_sales_this_month": total_sales,
        "active_enquiries": active_enquiries,
        "today_activities": today_activities
    }
