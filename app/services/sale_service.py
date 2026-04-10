from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime, date
import csv, io

from fastapi.responses import StreamingResponse

from app.models.sale import Sale
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale_payment import SalePayment

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


# =====================================================
# HELPERS
# =====================================================

def generate_invoice_number(db: Session, showroom_id: int):

    last = (
        db.query(Sale)
        .filter(Sale.showroom_id == showroom_id)
        .order_by(Sale.id.desc())
        .first()
    )

    if not last:
        return f"INV-{showroom_id}-1001"

    num = int(last.invoice_number.split("-")[-1]) + 1

    return f"INV-{showroom_id}-{num}"


# =====================================================
# CREATE SALE
# =====================================================

def create_sale(
    db: Session,
    showroom_id: int,
    customer_name: str,
    phone: str,
    address: str,
    product_id: int,
    quantity: int,
    order_amount: float,
    paid_amount: float,
    payment_type: str,
    sale_date: date,
    received_by: str,
    notes: str,
    created_by: str,
):

    customer = (
        db.query(Customer)
        .filter(
            Customer.showroom_id == showroom_id,
            Customer.phone == phone,
        )
        .first()
    )

    if not customer:
        customer = Customer(
            showroom_id=showroom_id,
            name=customer_name,
            phone=phone,
            address=address,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    product = db.get(Product, product_id)

    if not product:
        raise Exception("Product not found")

    if product.stock_qty < quantity:
        raise Exception("Insufficient stock")

    product.stock_qty -= quantity

    balance = order_amount - paid_amount
    invoice = generate_invoice_number(db, showroom_id)

    sale = Sale(
        showroom_id=showroom_id,
        invoice_number=invoice,
        customer_id=customer.id,
        product_id=product_id,
        quantity=quantity,
        order_amount=order_amount,
        paid_amount=paid_amount,
        balance_amount=balance,
        payment_type=payment_type,
        sale_date=sale_date,
        received_by=received_by,
        notes=notes,
    )

    db.add(sale)
    db.commit()
    db.refresh(sale)

    payment = SalePayment(
        sale_id=sale.id,
        amount=paid_amount,
        payment_type=payment_type,
        received_by=received_by,
        paid_at=datetime.utcnow(),
    )

    db.add(payment)
    db.commit()

    return {"success": True, "invoice": invoice}


# =====================================================
# LIST SALES
# =====================================================

def list_sales(
    db: Session,
    showroom_id: int,
    search: str,
    from_date: date,
    to_date: date,
    skip: int,
):

    q = (
        db.query(
            Sale,
            Customer.name.label("customer_name"),
            Product.product_name,
        )
        .join(Customer)
        .join(Product)
        .filter(Sale.showroom_id == showroom_id)
    )

    if search:
        q = q.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Sale.invoice_number.ilike(f"%{search}%"),
                Product.product_name.ilike(f"%{search}%"),
            )
        )

    if from_date:
        q = q.filter(Sale.sale_date >= from_date)

    if to_date:
        q = q.filter(Sale.sale_date <= to_date)

    total = q.count()

    rows = (
        q.order_by(Sale.id.desc())
        .offset(skip)
        .limit(10)
        .all()
    )

    items = []

    for sale, customer_name, product_name in rows:
        items.append({
            "id": sale.id,
            "invoice_number": sale.invoice_number,
            "customer_name": customer_name,
            "product_name": product_name,
            "quantity": sale.quantity,
            "order_amount": sale.order_amount,
            "paid_amount": sale.paid_amount,
            "balance_amount": sale.balance_amount,
            "payment_type": sale.payment_type,
            "sale_date": sale.sale_date,
            "status": sale.status,
        })

    return items, total


# =====================================================
# GET SALE
# =====================================================

def get_sale_by_id(db: Session, sale_id: int, showroom_id: int):

    sale = (
        db.query(Sale)
        .filter(
            Sale.id == sale_id,
            Sale.showroom_id == showroom_id,
        )
        .first()
    )

    if not sale:
        raise Exception("Sale not found")

    return {
        "id": sale.id,
        "invoice_number": sale.invoice_number,
        "customer": {
            "id": sale.customer.id,
            "name": sale.customer.name,
            "phone": sale.customer.phone,
            "address": sale.customer.address,
        },
        "product_id": sale.product_id,
        "product": {
            "product_name": sale.product.product_name
        },
        "quantity": sale.quantity,
        "order_amount": sale.order_amount,
        "paid_amount": sale.paid_amount,
        "balance_amount": sale.balance_amount,
        "payment_type": sale.payment_type,
        "sale_date": sale.sale_date,
        "received_by": sale.received_by,
        "notes": sale.notes,
        "status": sale.status,
        "payments": [
            {
                "amount": p.amount,
                "payment_type": p.payment_type,
                "received_by": p.received_by,
                "paid_at": p.paid_at,
            }
            for p in sale.payments
        ]
    }


# =====================================================
# DELETE SALE
# =====================================================

def delete_sale(db: Session, sale_id: int, showroom_id: int):

    sale = (
        db.query(Sale)
        .filter(
            Sale.id == sale_id,
            Sale.showroom_id == showroom_id,
        )
        .first()
    )

    if not sale:
        raise Exception("Sale not found")

    product = db.get(Product, sale.product_id)
    product.stock_qty += sale.quantity

    db.delete(sale)
    db.commit()


# =====================================================
# CSV EXPORT
# =====================================================

def export_sales_csv_file(db: Session, showroom_id: int):

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Invoice",
        "Customer",
        "Product",
        "Qty",
        "Order",
        "Paid",
        "Balance",
        "Date",
    ])

    rows = (
        db.query(Sale, Customer.name, Product.product_name)
        .join(Customer)
        .join(Product)
        .filter(Sale.showroom_id == showroom_id, Sale.status == "ACTIVE")
        .order_by(Sale.id.desc())
        .all()
    )

    for sale, customer, product in rows:
        writer.writerow([
            sale.invoice_number,
            customer,
            product,
            sale.quantity,
            sale.order_amount,
            sale.paid_amount,
            sale.balance_amount,
            sale.sale_date,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sales.csv"
        }
    )


# =====================================================
# ADD PAYMENT
# =====================================================

def add_payment_to_sale(db, sale, amount, payment_type, received_by, user_id):

    payment = SalePayment(
        sale_id=sale.id,
        amount=amount,
        payment_type=payment_type,
        received_by=received_by,
        paid_at=datetime.utcnow()
    )

    sale.paid_amount += amount
    sale.balance_amount -= amount

    db.add(payment)
    db.commit()
    db.refresh(sale)

    return {
        "success": True,
        "paid_amount": sale.paid_amount,
        "balance_amount": sale.balance_amount,
    }


# =====================================================
# CANCEL SALE
# =====================================================

def cancel_sale_and_restore_stock(db, sale, cancelled_by):

    product = db.get(Product, sale.product_id)

    if product:
        product.stock_qty += sale.quantity

    sale.status = "CANCELLED"

    db.query(SalePayment).filter(
        SalePayment.sale_id == sale.id
    ).delete()

    db.commit()

    return {"success": True}


# =====================================================
# INVOICE PDF (UPDATED ONLY HERE)
# =====================================================

def generate_invoice_pdf(db: Session, sale: Sale):

    customer = sale.customer
    product = sale.product

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    c.rect(10, 10, width - 20, height - 20)

    c.rect(15, height - 80, 80, 50)
    c.drawString(20, height - 60, "LOGO")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(110, height - 40, "ZHAGARAM MOTORS")

    c.setFont("Helvetica", 8)
    c.drawString(110, height - 55, "No:11, Vellore, Tamil Nadu")
    c.drawString(110, height - 65, "GSTIN: 33XXXXXXXXXX")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(420, height - 50, "TAX INVOICE")

    c.rect(15, height - 130, width - 30, 40)

    c.setFont("Helvetica", 9)
    c.drawString(20, height - 105, f"Invoice No: {sale.invoice_number}")
    c.drawString(20, height - 120, f"Date: {sale.sale_date}")

    c.drawString(300, height - 105, "Place Of Supply: Tamil Nadu")
    c.drawString(300, height - 120, "Terms: Due on Receipt")

    c.rect(15, height - 200, (width - 30) / 2, 60)
    c.rect(15 + (width - 30) / 2, height - 200, (width - 30) / 2, 60)

    c.setFont("Helvetica", 8)
    c.drawString(20, height - 165, customer.name)

    # ================= TABLE =================
    table_y = height - 230

    c.rect(15, table_y - 80, width - 30, 80)

    gst_percent = 5
    tax = sale.order_amount * gst_percent / 100
    cgst = tax / 2
    sgst = tax / 2

    c.setFont("Helvetica", 8)

    # PRODUCT NAME
    c.drawString(20, table_y - 35, product.product_name)

    # ✅ NEW: NOTES BELOW PRODUCT
    if sale.notes:
        c.setFont("Helvetica", 7)
        c.drawString(20, table_y - 48, f"Note: {sale.notes}")
        c.setFont("Helvetica", 8)

    c.drawString(250, table_y - 35, str(sale.quantity))
    c.drawString(290, table_y - 35, str(product.sale_price))
    c.drawString(450, table_y - 35, str(sale.order_amount))

    c.showPage()
    c.save()

    buffer.seek(0)

    return buffer, f"{sale.invoice_number}.pdf"

# =====================================================
# DASHBOARD - DAILY
# =====================================================

def get_daily_sales_dashboard(db: Session, showroom_id: int, target_date: date):

    sales = (
        db.query(Sale)
        .filter(
            Sale.showroom_id == showroom_id,
            Sale.sale_date == target_date,
        )
        .all()
    )

    total_sales = sum(s.order_amount for s in sales)
    total_paid = sum(s.paid_amount for s in sales)
    total_balance = sum(s.balance_amount for s in sales)

    invoices = len(sales)

    cancelled = len([s for s in sales if s.status == "CANCELLED"])

    return {
        "date": target_date,
        "total_sales": total_sales,
        "total_paid": total_paid,
        "total_balance": total_balance,
        "invoices": invoices,
        "cancelled": cancelled,
    }


# =====================================================
# DASHBOARD - RANGE
# =====================================================

def get_range_sales_dashboard(
    db: Session,
    showroom_id: int,
    from_date: date,
    to_date: date,
):

    rows = (
        db.query(
            Product.product_name,
            func.sum(Sale.quantity).label("qty"),
            func.sum(Sale.order_amount).label("amount"),
        )
        .join(Sale)
        .filter(
            Sale.showroom_id == showroom_id,
            Sale.sale_date.between(from_date, to_date),
            Sale.status == "ACTIVE",
        )
        .group_by(Product.product_name)
        .all()
    )

    return [
        {
            "product": r.product_name,
            "qty": r.qty,
            "amount": r.amount,
        }
        for r in rows
    ]