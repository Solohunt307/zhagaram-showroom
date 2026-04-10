# app/api/v1/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.showroom import Showroom
from app.core.deps import get_current_user
from app.schemas.auth import LoginRequest, LoginResponse
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    # ✅ LOGIN BY USERNAME
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # ✅ HANDLE NULL is_active (VERY IMPORTANT)
    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # ✅ PASSWORD CHECK (MATCH YOUR DB COLUMN)
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "showroom_id": user.showroom_id,
    }

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "role": user.role,
        "showroom_required": user.role == "ADMIN",
    }


@router.get("/showrooms")
def get_showrooms(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(403, "Not allowed")

    return db.query(Showroom).all()


@router.post("/select-showroom/{showroom_id}")
def select_showroom(
    showroom_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    user = db.query(User).filter(User.id == int(current_user["sub"])).first()

    if not user:
        raise HTTPException(404, "User not found")

    user.showroom_id = showroom_id
    db.commit()

    token_data = {
        "sub": str(user.id),
        "role": user.role,
        "showroom_id": showroom_id,
    }

    new_token = create_access_token(token_data)

    return {
        "access_token": new_token,
        "message": "Showroom selected",
    }

