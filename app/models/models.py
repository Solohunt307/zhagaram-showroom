from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# ------------------ Showroom ------------------
class Showroom(Base):
    __tablename__ = "showrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    location = Column(String(150))

# ------------------ Users ------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(String(20))  # Admin / Manager / Technician
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    is_active = Column(Boolean, default=True)

    showroom = relationship("Showroom")

# ------------------ Products ------------------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    product_name = Column(String(100), nullable=False)
    hsn = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    variant = Column(String(50), nullable=False)
    color = Column(String(50), nullable=False)
    purchase_price = Column(Float)
    sale_price = Column(Float, nullable=False)
    tax_rate = Column(Float)
    stock_qty = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=0)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

# ------------------ Vendors ------------------
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    name = Column(String(100), nullable=False)
    mobile = Column(String(15), nullable=False)
    email = Column(String(100), nullable=False)
    gst_no = Column(String(50))
    location = Column(String(150), nullable=False)

# ------------------ Purchases ------------------
class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    quantity = Column(Integer)
    color = Column(String(50))
    amount = Column(Float)
    payment_mode = Column(String(20))
    shipment_mode = Column(String(50))
    notes = Column(Text)
    file_path = Column(String(255))
    purchase_date = Column(Date)

# ------------------ Customers ------------------
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    email = Column(String(100))
    phone = Column(String(15), nullable=False)

# ------------------ Sales ------------------
class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    order_amount = Column(Float)
    paid_amount = Column(Float)
    balance_amount = Column(Float)
    payment_type = Column(String(20))
    invoice_number = Column(String(50), unique=True)
    sale_date = Column(Date)
    received_by = Column(String(100))
    notes = Column(Text)

# ------------------ Sale Payments ------------------
class SalePayment(Base):
    __tablename__ = "sale_payments"
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    payment_date = Column(Date)
    payment_type = Column(String(20))
    amount = Column(Float)
    received_by = Column(String(100))

# ------------------ Employees ------------------
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    emp_id = Column(String(50))
    name = Column(String(100))
    address = Column(Text)
    mobile = Column(String(15))
    email = Column(String(100))
    role = Column(String(20))
    file_path = Column(String(255))

# ------------------ Employee Activities ------------------
class EmployeeActivity(Base):
    __tablename__ = "employee_activities"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    working_hours = Column(Float)
    salary_per_month = Column(Float)
    salary_paid = Column(Float)
    payment_type = Column(String(20))
    date = Column(Date)

# ------------------ Service Tickets ------------------
class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    technician_id = Column(Integer, ForeignKey("employees.id"))
    complaint = Column(Text)
    resolved_complaint = Column(Text)
    unresolved_complaint = Column(Text)
    ticket_status = Column(String(20))
    created_date = Column(Date)
    closed_date = Column(Date)
    service_cost = Column(Float)
    amount_paid = Column(Float)
    balance = Column(Float)
    payment_mode = Column(String(20))
    file_path = Column(String(255))

# ------------------ Expenses ------------------
class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"))
    description = Column(Text)
    expense_type = Column(String(50))  # Monthly / Daily
    amount = Column(Float)
    date = Column(Date)
    done_by = Column(String(100))
