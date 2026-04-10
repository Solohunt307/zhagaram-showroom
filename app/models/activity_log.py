from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from app.core.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    module = Column(String(50))  # SALES / INVENTORY / SERVICE / EMPLOYEE etc

    message = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
