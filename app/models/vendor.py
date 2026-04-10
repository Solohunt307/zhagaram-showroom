from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Boolean
from app.core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    name = Column(String(150), nullable=False)
    mobile = Column(String(20), nullable=False)
    email = Column(String(150))
    gst_no = Column(String(50))
    is_active = Column(Boolean, default=True)
    location = Column(String(150), nullable=False)
