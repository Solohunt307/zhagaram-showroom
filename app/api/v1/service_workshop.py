from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import shutil
import os

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.service_ticket import (
    ServiceTicketCreate,
    ServiceTicketOut,
)
from app.models.service_ticket import ServiceTicket
from app.services.service_ticket_service import (
    create_ticket,
    close_ticket,
)

UPLOAD_DIR = "uploads/service"
os.makedirs(UPLOAD_DIR, exist_ok=True)

#router = APIRouter(prefix="/service", tags=["Service & Workshop"])
router = APIRouter(prefix="/service", tags=["Service"])


@router.post("/", response_model=ServiceTicketOut)
def create_service_ticket(
    data: ServiceTicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_ticket(
        db,
        current_user["showroom_id"],
        data,
        current_user["sub"]
    )


@router.put("/{ticket_id}", response_model=ServiceTicketOut)
def update_service_ticket(
    ticket_id: int,
    data: ServiceTicketCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    ticket = (
        db.query(ServiceTicket)
        .filter(
            ServiceTicket.id == ticket_id,
            ServiceTicket.showroom_id == current_user["showroom_id"]
        )
        .first()
    )

    if not ticket:
        raise HTTPException(404, "Ticket not found")

    return close_ticket(db, ticket, data, current_user["sub"])
