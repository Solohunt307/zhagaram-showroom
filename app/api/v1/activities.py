from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.activity_log import ActivityLog

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("/")
def get_activity_feed(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 20
):
    showroom_id = current_user["showroom_id"]

    activities = (
        db.query(ActivityLog)
        .filter(ActivityLog.showroom_id == showroom_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return activities
