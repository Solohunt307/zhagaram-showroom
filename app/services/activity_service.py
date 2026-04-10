from sqlalchemy.orm import Session
from datetime import datetime

from app.models.activity_log import ActivityLog


def log_activity(
    db: Session,
    showroom_id: int,
    user_id: int,
    module: str,
    message: str,
):

    log = ActivityLog(
        showroom_id=showroom_id,
        user_id=user_id,
        module=module,
        message=message,
        created_at=datetime.utcnow(),
    )

    db.add(log)
    db.commit()
