from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import get_password_hash

from app.models.user import User
from app.models.showroom import Showroom

from app.schemas.user import UserCreate, PasswordUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# CREATE USER
# =========================
@router.post("")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "ADMIN":
        raise HTTPException(403, "Only admin allowed")

    existing = db.query(User).filter(User.username == data.username).first()

    if existing:
        raise HTTPException(400, "Username already exists")

    new_user = User(
        name=data.name,
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=data.role,
        showroom_id=data.showroom_id
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created"}


# =========================
# GET USERS
# =========================
@router.get("")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "ADMIN":
        raise HTTPException(403, "Only admin allowed")

    users = db.query(User).all()

    result = []

    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "username": u.username,
            "role": u.role,
            "showroom_name": u.showroom.name if u.showroom else None
        })

    return result


# =========================
# DELETE USER
# =========================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "ADMIN":
        raise HTTPException(403, "Only admin allowed")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}


# =========================
# CHANGE PASSWORD
# =========================
@router.put("/{user_id}/password")
def change_password(
    user_id: int,
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "ADMIN":
        raise HTTPException(403, "Only admin allowed")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "User not found")

    user.password_hash = get_password_hash(data.password)

    db.commit()

    return {"message": "Password updated"}