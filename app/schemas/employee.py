from pydantic import BaseModel
from typing import Optional
from datetime import date


class EmployeeCreate(BaseModel):
    emp_code: str
    name: str
    address: Optional[str]
    mobile: Optional[str]
    email: Optional[str]
    role: str


class EmployeeOut(EmployeeCreate):
    id: int
    file_path: Optional[str]

    class Config:
        from_attributes = True


class EmployeeActivityCreate(BaseModel):
    employee_id: int
    total_hours: float
    salary_per_month: float
    salary_paid: float
    activity_date: date
    payment_type: str


class EmployeeActivityOut(EmployeeActivityCreate):
    id: int

    class Config:
        from_attributes = True
