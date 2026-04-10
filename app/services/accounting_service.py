from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.expense import Expense  # Will be created in Expenses module


def get_accounting_summary(
    db: Session,
    showroom_id: int,
    from_date,
    to_date,
):

    total_sales = db.query(Sale).filter(
        Sale.showroom_id == showroom_id,
        Sale.sale_date.between(from_date, to_date)
    )

    total_purchases = db.query(Purchase).filter(
        Purchase.showroom_id == showroom_id,
        Purchase.purchase_date.between(from_date, to_date)
    )

    sales_amount = total_sales.with_entities(
        func.sum(Sale.order_amount)
    ).scalar() or 0

    purchase_amount = total_purchases.with_entities(
        func.sum(Purchase.amount)
    ).scalar() or 0

    total_sales_count = total_sales.count()
    total_purchase_count = total_purchases.count()

    # EXPENSES (future module)
    expenses = (
        db.query(func.sum(Expense.amount))
        .filter(
            Expense.showroom_id == showroom_id,
            Expense.expense_date.between(from_date, to_date)
        )
        .scalar() or 0
    )

    net_profit = sales_amount - purchase_amount - expenses

    return {
        "total_sales": total_sales_count,
        "total_purchases": total_purchase_count,
        "total_sales_amount": sales_amount,
        "total_purchase_amount": purchase_amount,
        "total_expenses": expenses,
        "net_profit": net_profit,
    }
