from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_stock: int
    low_stock_alerts: int
    vehicles_sold_this_month: int
    total_sales_this_month: float
    active_enquiries: int
    today_activities: int
