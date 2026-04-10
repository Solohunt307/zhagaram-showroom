from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from sqlalchemy.orm import Session

import shutil
import os
import uuid
from pathlib import Path
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeOut,
    EmployeeActivityCreate,
    EmployeeActivityOut,
)

from app.services.employee_service import (
    create_employee,
    update_employee,
    delete_employee,
    list_employees,
    create_activity,
    list_activities,
    update_activity,
    delete_activity,
    export_activity_csv,
    export_employees_csv,   # ✅ ADDED
)

from app.models.employee import Employee
from app.models.employee_activity import EmployeeActivity


# =====================================================
# FILE UPLOAD CONFIG
# =====================================================

UPLOAD_DIR = "uploads/employees"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/employees", tags=["Employees"])


# =====================================================
# CREATE EMPLOYEE
# =====================================================

@router.post("/", response_model=EmployeeOut)
def add_employee(
    emp_code: str = Form(...),
    name: str = Form(...),
    address: str = Form(None),
    mobile: str = Form(None),
    email: str = Form(None),
    role: str = Form(...),
    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    file_path = None

    if file and file.filename:
        ext = Path(file.filename).suffix
        safe_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(UPLOAD_DIR, safe_name)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_path = path

    data = EmployeeCreate(
        emp_code=emp_code,
        name=name,
        address=address,
        mobile=mobile,
        email=email,
        role=role,
    )

    return create_employee(
        db,
        current_user["showroom_id"],
        data,
        file_path,
        current_user["sub"],
    )


# =====================================================
# LIST EMPLOYEES
# =====================================================

@router.get("/")
def get_employees(
    search: str | None = None,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_employees(
        db,
        current_user["showroom_id"],
        search,
        skip,
    )

    return {"items": items, "total": total}


@router.get("/dropdown")
def employee_dropdown(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rows = (
        db.query(Employee.id, Employee.name)
        .filter(Employee.showroom_id == current_user["showroom_id"])
        .all()
    )

    return [{"id": r.id, "name": r.name} for r in rows]

@router.get("/activities")
def get_activities(
    search: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    page: int = 1,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    skip = (page - 1) * 10

    items, total = list_activities(
        db,
        current_user["showroom_id"],
        search,
        from_date,
        to_date,
        skip,
    )

    return {"items": items, "total": total}

# =====================================================
# GET SINGLE EMPLOYEE (🔥 FIX FOR EDIT)
# =====================================================

@router.get("/{emp_id}", response_model=EmployeeOut)
def get_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    emp = (
        db.query(Employee)
        .filter(
            Employee.id == emp_id,
            Employee.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not emp:
        raise HTTPException(404, "Employee not found")

    return emp


# =====================================================
# UPDATE EMPLOYEE
# =====================================================

@router.put("/{emp_id}", response_model=EmployeeOut)
def edit_employee(
    emp_id: int,

    emp_code: str = Form(...),
    name: str = Form(...),
    address: str = Form(None),
    mobile: str = Form(None),
    email: str = Form(None),
    role: str = Form(...),

    file: UploadFile | None = File(None),

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    emp = (
        db.query(Employee)
        .filter(
            Employee.id == emp_id,
            Employee.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not emp:
        raise HTTPException(404, "Employee not found")

    file_path = emp.file_path

    if file and file.filename:
        ext = Path(file.filename).suffix
        safe_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(UPLOAD_DIR, safe_name)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_path = path

    data = EmployeeCreate(
        emp_code=emp_code,
        name=name,
        address=address,
        mobile=mobile,
        email=email,
        role=role,
    )

    return update_employee(
        db,
        emp,
        data,
        file_path,
        current_user["sub"],
    )


# =====================================================
# DELETE EMPLOYEE
# =====================================================

@router.delete("/{emp_id}")
def remove_employee(
    emp_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    emp = (
        db.query(Employee)
        .filter(
            Employee.id == emp_id,
            Employee.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not emp:
        raise HTTPException(404, "Employee not found")

    delete_employee(db, emp, current_user["sub"])

    return {"message": "Deleted"}


# =====================================================
# EXPORT EMPLOYEES CSV (🔥 FIX)
# =====================================================

@router.get("/export/csv")
def export_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return export_employees_csv(db, current_user["showroom_id"])


# =====================================================
# CREATE ACTIVITY
# =====================================================

@router.post("/activity", response_model=EmployeeActivityOut)
def add_activity(
    data: EmployeeActivityCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return create_activity(
        db,
        current_user["showroom_id"],
        data,
        current_user["sub"],
    )


# =====================================================
# LIST ACTIVITIES
# =====================================================




# =====================================================
# UPDATE ACTIVITY
# =====================================================

@router.put("/activity/{act_id}")
def edit_activity(
    act_id: int,
    data: EmployeeActivityCreate,

    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    act = (
        db.query(EmployeeActivity)
        .filter(
            EmployeeActivity.id == act_id,
            EmployeeActivity.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not act:
        raise HTTPException(404, "Activity not found")

    return update_activity(db, act, data, current_user["sub"])


# =====================================================
# DELETE ACTIVITY
# =====================================================

@router.delete("/activity/{act_id}")
def remove_activity(
    act_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    act = (
        db.query(EmployeeActivity)
        .filter(
            EmployeeActivity.id == act_id,
            EmployeeActivity.showroom_id == current_user["showroom_id"],
        )
        .first()
    )

    if not act:
        raise HTTPException(404, "Activity not found")

    delete_activity(db, act, current_user["sub"])

    return {"message": "Deleted"}


# =====================================================
# EXPORT ACTIVITIES CSV
# =====================================================

@router.get("/activities/export/csv")
def export_activity(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return export_activity_csv(db, current_user["showroom_id"])

