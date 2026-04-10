from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.showroom import Showroom
from app.core.security import create_access_token


router = APIRouter(prefix="/showrooms", tags=["Showrooms"])


@router.get("/")
def list_showrooms(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(Showroom).all()




@router.post("/select/{showroom_id}")
def select_showroom(
    showroom_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    showroom = db.query(Showroom).filter(Showroom.id == showroom_id).first()
    if not showroom:
        raise HTTPException(status_code=404, detail="Showroom not found")

    token_data = {
        "sub": current_user["sub"],
        "role": "ADMIN",
        "showroom_id": showroom_id
    }

    access_token = create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "showroom": showroom.name
    }

