from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False)

    emp_code = Column(String(50), unique=True)
    name = Column(String(150), nullable=False)
    address = Column(String(255))
    mobile = Column(String(30))
    email = Column(String(150))

    role = Column(String(50))

    file_path = Column(String(255))
