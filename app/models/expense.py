from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.core.database import Base


class Expense(Base):

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    showroom_id = Column(Integer, nullable=False)

    category = Column(String(50), nullable=False)

    description = Column(String(255))

    amount = Column(Float, nullable=False)

    expense_date = Column(Date, nullable=False)

    created_by = Column(Integer, nullable=False)
