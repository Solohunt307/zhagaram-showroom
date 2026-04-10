from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date
from app.core.database import Base


class EmployeeActivity(Base):
    __tablename__ = "employee_activities"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    employee_id = Column(Integer, ForeignKey("employees.id"))

    total_hours = Column(Float)
    salary_per_month = Column(Float)
    salary_paid = Column(Float)

    activity_date = Column(Date)

    payment_type = Column(String(50))
