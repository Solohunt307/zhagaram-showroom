# create_tables.py

from app.core.database import engine, Base
from dotenv import load_dotenv

load_dotenv()

# 🔥 IMPORT ALL MODELS (MANDATORY)
from app.models.user import User
from app.models.showroom import Showroom
from app.models.product import Product
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.purchase import Purchase
from app.models.sale import Sale
from app.models.sale_payment import SalePayment
from app.models.expense import Expense
from app.models.service_ticket import ServiceTicket
from app.models.employee import Employee
from app.models.employee_activity import EmployeeActivity
from app.models.activity_log import ActivityLog
from app.models.enquiry import Enquiry
from app.models.vehicle import Vehicle

# ✅ CREATE TABLES
Base.metadata.create_all(bind=engine)

print("Connecting to DB...")
conn = engine.connect()
print("✅ Connected successfully!")
conn.close()

print("✅ All tables created successfully in TiDB")
