from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.core.database import engine, Base

# Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.showrooms import router as showroom_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.activities import router as activities_router
from app.api.v1.products import router as product_router
from app.api.v1.purchases import router as purchases_router
from app.api.v1.customers import router as customers_router
from app.api.v1.sales import router as sales_router
from app.api.v1.service_tickets import router as service_router
from app.api.v1.employees import router as employees_router
from app.api.v1.accounting import router as accounting_router
from app.api.v1.reports import router as reports_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.users import router as user_router

app = FastAPI(title="Zhagaram Showroom Management")

# ✅ Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Root redirect
@app.get("/")
def root():
    return RedirectResponse("/static/login.html")

# ✅ CORS (important for Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register routers
app.include_router(auth_router)
app.include_router(showroom_router)
app.include_router(dashboard_router)
app.include_router(activities_router)
app.include_router(product_router)
app.include_router(purchases_router)
app.include_router(sales_router)
app.include_router(customers_router)
app.include_router(service_router)
app.include_router(employees_router)
app.include_router(accounting_router)
app.include_router(reports_router)
app.include_router(expenses_router)
app.include_router(user_router)