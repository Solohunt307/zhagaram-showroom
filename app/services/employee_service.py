from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.models.employee import Employee
from app.models.employee_activity import EmployeeActivity
from app.services.activity_service import log_activity


# =====================================================
# CREATE EMPLOYEE
# =====================================================

def create_employee(db: Session, showroom_id: int, data, file_path, user_id):

    try:

        emp = Employee(
            showroom_id=showroom_id,
            file_path=file_path,
            **data.dict()
        )

        db.add(emp)
        db.commit()
        db.refresh(emp)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Employee code already exists"
        )

    log_activity(
        db,
        showroom_id,
        user_id,
        "EMPLOYEE",
        f"Employee added: {emp.name}"
    )

    return emp


# =====================================================
# UPDATE EMPLOYEE
# =====================================================

def update_employee(db, emp, data, file_path, user_id):

    # ✅ check duplicate ONLY if changed
    if emp.emp_code != data.emp_code:
        existing = (
            db.query(Employee)
            .filter(
                Employee.emp_code == data.emp_code,
                Employee.id != emp.id   # 🔥 IMPORTANT
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Employee code already exists"
            )

    for k, v in data.dict().items():
        setattr(emp, k, v)

    if file_path:
        emp.file_path = file_path

    db.commit()
    db.refresh(emp)

    log_activity(
        db,
        emp.showroom_id,
        user_id,
        "EMPLOYEE",
        f"Employee updated: {emp.name}"
    )

    return emp


# =====================================================
# DELETE EMPLOYEE
# =====================================================

def delete_employee(db, emp, user_id):

    db.delete(emp)
    db.commit()

    log_activity(
        db,
        emp.showroom_id,
        user_id,
        "EMPLOYEE",
        f"Employee deleted: {emp.name}"
    )


# =====================================================
# LIST EMPLOYEES
# =====================================================

def list_employees(db, showroom_id, search=None, skip=0, limit=10):

    q = db.query(Employee).filter(Employee.showroom_id == showroom_id)

    if search:
        q = q.filter(
            or_(
                Employee.name.ilike(f"%{search}%"),
                Employee.emp_code.ilike(f"%{search}%"),
                Employee.mobile.ilike(f"%{search}%"),
            )
        )

    total = q.count()

    return (
        q.order_by(Employee.name.asc())
        .offset(skip)
        .limit(limit)
        .all(),
        total,
    )


# =====================================================
# EXPORT EMPLOYEES CSV
# =====================================================

def export_employees_csv(db, showroom_id):

    rows = (
        db.query(Employee)
        .filter(Employee.showroom_id == showroom_id)
        .order_by(Employee.name.asc())
        .all()
    )

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "Emp Code",
        "Name",
        "Address",
        "Mobile",
        "Email",
        "Role",
    ])

    for e in rows:
        writer.writerow([
            e.emp_code,
            e.name,
            e.address or "",
            e.mobile or "",
            e.email or "",
            e.role,
        ])

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=employees.csv"
        },
    )


# =====================================================
# CREATE ACTIVITY
# =====================================================

def create_activity(db: Session, showroom_id: int, data, user_id):

    act = EmployeeActivity(
        showroom_id=showroom_id,
        **data.dict()
    )

    db.add(act)
    db.commit()
    db.refresh(act)

    log_activity(
        db,
        showroom_id,
        user_id,
        "EMPLOYEE",
        f"Salary activity recorded for employee ID {act.employee_id}"
    )

    return act


# =====================================================
# LIST ACTIVITIES
# =====================================================

def list_activities(
    db,
    showroom_id,
    search=None,
    from_date=None,
    to_date=None,
    skip=0,
    limit=10,
):

    q = (
        db.query(EmployeeActivity, Employee.name)
        .join(Employee, Employee.id == EmployeeActivity.employee_id)
        .filter(EmployeeActivity.showroom_id == showroom_id)
    )

    if search:
        q = q.filter(Employee.name.ilike(f"%{search}%"))

    if from_date:
        q = q.filter(EmployeeActivity.activity_date >= from_date)

    if to_date:
        q = q.filter(EmployeeActivity.activity_date <= to_date)

    total = q.count()

    rows = (
        q.order_by(EmployeeActivity.activity_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []

    for act, name in rows:

        d = act.__dict__.copy()
        d.pop("_sa_instance_state", None)
        d["employee_name"] = name

        items.append(d)

    return items, total


# =====================================================
# UPDATE ACTIVITY
# =====================================================

def update_activity(db: Session, activity, data, user_id):

    for k, v in data.dict().items():
        setattr(activity, k, v)

    db.commit()
    db.refresh(activity)

    log_activity(
        db,
        activity.showroom_id,
        user_id,
        "EMPLOYEE",
        f"Activity updated for employee ID {activity.employee_id}"
    )

    return activity


# =====================================================
# DELETE ACTIVITY
# =====================================================

def delete_activity(db: Session, activity, user_id):

    db.delete(activity)
    db.commit()

    log_activity(
        db,
        activity.showroom_id,
        user_id,
        "EMPLOYEE",
        f"Activity deleted for employee ID {activity.employee_id}"
    )


# =====================================================
# EXPORT ACTIVITY CSV
# =====================================================

def export_activity_csv(db, showroom_id):

    rows = (
        db.query(EmployeeActivity, Employee.name)
        .join(Employee, Employee.id == EmployeeActivity.employee_id)
        .filter(EmployeeActivity.showroom_id == showroom_id)
        .order_by(EmployeeActivity.activity_date.desc())
        .all()
    )

    buffer = StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "Employee Name",
        "Total Hours",
        "Salary Per Month",
        "Salary Paid",
        "Date",
        "Payment Type",
    ])

    for act, name in rows:
        writer.writerow([
            name,
            act.total_hours,
            act.salary_per_month,
            act.salary_paid,
            act.activity_date,
            act.payment_type,
        ])

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=employee_activities.csv"
        },
    )
