from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import csv, io

from app.models.sale import Sale
from app.models.product import Product
from app.models.customer import Customer


# =====================================================
# SALES SUMMARY
# =====================================================

def get_sales_summary(db: Session, showroom_id: int, from_date: date, to_date: date):

    sales = db.query(Sale).filter(
        Sale.showroom_id == showroom_id,
        Sale.sale_date.between(from_date, to_date),
        Sale.status == "ACTIVE"
    ).all()

    total = sum(s.order_amount or 0 for s in sales)
    count = len(sales)

    return {
        "total_sales": total,
        "invoices": count,
        "avg_order": round(total / count, 2) if count else 0
    }


# =====================================================
# TOP PRODUCTS
# =====================================================

def get_top_products(db: Session, showroom_id: int):

    rows = db.query(
        Product.product_name,
        func.sum(Sale.quantity).label("qty"),
        func.sum(Sale.order_amount).label("revenue")
    ).join(Sale).filter(
        Sale.showroom_id == showroom_id,
        Sale.status == "ACTIVE"
    ).group_by(Product.product_name).all()

    return [
        {
            "product": r.product_name,
            "qty": int(r.qty or 0),
            "revenue": float(r.revenue or 0)
        }
        for r in rows
    ]


# =====================================================
# SHOWROOM
# =====================================================

def get_sales_by_showroom(db: Session):

    rows = db.query(
        Sale.showroom_id,
        func.sum(Sale.order_amount).label("total")
    ).filter(
        Sale.status == "ACTIVE"
    ).group_by(Sale.showroom_id).all()

    return [
        {
            "showroom": r.showroom_id,
            "total": float(r.total or 0)
        }
        for r in rows
    ]


# =====================================================
# EMPLOYEE
# =====================================================

def get_sales_by_employee(db: Session, showroom_id: int):

    rows = db.query(
        Sale.received_by,
        func.count(Sale.id),
        func.sum(Sale.order_amount)
    ).filter(
        Sale.showroom_id == showroom_id,
        Sale.status == "ACTIVE"
    ).group_by(Sale.received_by).all()

    return [
        {
            "employee": r[0],
            "count": int(r[1] or 0),
            "total": float(r[2] or 0)
        }
        for r in rows
    ]


# =====================================================
# PROFIT
# =====================================================

def get_profit_analysis(db: Session, showroom_id: int):

    rows = db.query(Sale).filter(
        Sale.showroom_id == showroom_id,
        Sale.status == "ACTIVE"
    ).all()

    sales = 0
    cost = 0

    for s in rows:
        product = s.product
        if not product:
            continue

        sales += s.order_amount or 0
        cost += (product.purchase_price or 0) * s.quantity

    return {
        "sales": sales,
        "purchase": cost,
        "expenses": 0,
        "profit": sales - cost
    }


# =====================================================
# FORECAST
# =====================================================

def forecast_demand(db: Session, showroom_id: int):

    last_90 = date.today() - timedelta(days=90)

    rows = db.query(
        Product.product_name,
        func.sum(Sale.quantity)
    ).join(Sale).filter(
        Sale.showroom_id == showroom_id,
        Sale.sale_date >= last_90,
        Sale.status == "ACTIVE"
    ).group_by(Product.product_name).all()

    return [
        {
            "product": r[0],
            "forecast": int((r[1] or 0) / 3)
        }
        for r in rows
    ]


# =====================================================
# CUSTOMER
# =====================================================

def get_customer_patterns(db: Session, showroom_id: int):

    rows = db.query(
        Customer.name,
        func.count(Sale.id),
        func.sum(Sale.order_amount)
    ).join(Sale).filter(
        Sale.showroom_id == showroom_id,
        Sale.status == "ACTIVE"
    ).group_by(Customer.name).all()

    return [
        {
            "customer": r[0],
            "orders": int(r[1] or 0),
            "total": float(r[2] or 0)
        }
        for r in rows
    ]


# =====================================================
# TREND
# =====================================================

def get_sales_trend(db: Session, showroom_id: int, days: int):

    start = date.today() - timedelta(days=days)

    rows = db.query(
        Sale.sale_date,
        func.sum(Sale.order_amount)
    ).filter(
        Sale.showroom_id == showroom_id,
        Sale.sale_date >= start,
        Sale.status == "ACTIVE"
    ).group_by(Sale.sale_date).all()

    return [
        {
            "date": r[0],
            "revenue": float(r[1] or 0)
        }
        for r in rows
    ]


# =====================================================
# CSV
# =====================================================

def export_reports_csv(data, headers):

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)

    for row in data:
        writer.writerow(row)

    return {"csv": output.getvalue()}


def apply_filters(query, Sale, showroom_id, params):
    if showroom_id:
        query = query.filter(Sale.showroom_id == showroom_id)

    if params.get("from_date"):
        query = query.filter(Sale.sale_date >= params["from_date"])

    if params.get("to_date"):
        query = query.filter(Sale.sale_date <= params["to_date"])

    query = query.filter(Sale.status == "ACTIVE")

    return query

def get_kpi_summary(db, showroom_id, params):

    query = db.query(Sale)
    query = apply_filters(query, Sale, showroom_id, params)

    rows = query.all()

    total_sales = sum(s.order_amount or 0 for s in rows)
    total_invoices = len(rows)
    avg_order = total_sales / total_invoices if total_invoices else 0

    return {
        "total_sales": total_sales,
        "total_invoices": total_invoices,
        "avg_order_value": round(avg_order, 2)
    }

def get_sales_trend_advanced(db, showroom_id, params, group_by):

    query = db.query(
        Sale.sale_date,
        func.sum(Sale.order_amount)
    )

    query = apply_filters(query, Sale, showroom_id, params)

    if group_by == "monthly":
        query = db.query(
            func.date_format(Sale.sale_date, "%Y-%m"),
            func.sum(Sale.order_amount)
        )

    rows = query.group_by(Sale.sale_date).all()

    return {
        "labels": [str(r[0]) for r in rows],
        "data": [float(r[1] or 0) for r in rows]
    }

def paginate(query, page, limit):
    total = query.count()
    items = query.offset((page-1)*limit).limit(limit).all()
    return items, total


def get_top_products_advanced(db, showroom_id, params):

    query = db.query(
        Product.product_name,
        func.sum(Sale.quantity).label("qty"),
        func.sum(Sale.order_amount).label("revenue")
    ).join(Sale)

    query = apply_filters(query, Sale, showroom_id, params)

    query = query.group_by(Product.product_name)

    items, total = paginate(query, params["page"], params["limit"])

    result = [
        {
            "product": r.product_name,
            "qty": int(r.qty or 0),
            "revenue": float(r.revenue or 0)
        }
        for r in items
    ]

    return {
        "data": result,
        "total": total
    }

def get_employee_performance(db, showroom_id, params):

    query = db.query(
        Sale.received_by,
        func.count(Sale.id),
        func.sum(Sale.order_amount)
    )

    query = apply_filters(query, Sale, showroom_id, params)

    query = query.group_by(Sale.received_by)

    items, total = paginate(query, params["page"], params["limit"])

    return {
        "data": [
            {
                "employee": r[0],
                "invoices": r[1],
                "revenue": float(r[2] or 0)
            }
            for r in items
        ],
        "total": total
    }

def get_showroom_performance(db, params):

    query = db.query(
        Sale.showroom_id,
        func.sum(Sale.order_amount)
    )

    query = apply_filters(query, Sale, None, params)

    query = query.group_by(Sale.showroom_id)

    rows = query.all()

    return [
        {
            "showroom": r[0],
            "revenue": float(r[1] or 0)
        }
        for r in rows
    ]


def get_profit_advanced(db, showroom_id, params):

    query = db.query(Sale)
    query = apply_filters(query, Sale, showroom_id, params)

    rows = query.all()

    revenue = 0
    cost = 0

    for s in rows:
        if not s.product:
            continue

        revenue += s.order_amount or 0
        cost += (s.product.purchase_price or 0) * s.quantity

    return {
        "revenue": revenue,
        "cost": cost,
        "profit": revenue - cost
    }

def get_export_data(db, showroom_id, type, params):

    if type == "top_products":
        result = get_top_products_advanced(db, showroom_id, params)["data"]
        headers = ["Product", "Qty", "Revenue"]
        data = [[r["product"], r["qty"], r["revenue"]] for r in result]

    elif type == "employees":
        result = get_employee_performance(db, showroom_id, params)["data"]
        headers = ["Employee", "Invoices", "Revenue"]
        data = [[r["employee"], r["invoices"], r["revenue"]] for r in result]

    else:
        raise Exception("Invalid type")

    return data, headers

