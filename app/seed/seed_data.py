from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.showroom import Showroom
from app.core.security import get_password_hash


def seed():

    db: Session = SessionLocal()

    print("🌱 Seeding database...")

    # Create showrooms
    vellore = Showroom(name="Vellore Showroom", location="Vellore")
    gudiyatham = Showroom(name="Gudiyatham Showroom", location="Gudiyatham")

    db.add_all([vellore, gudiyatham])
    db.commit()

    # Create admin
    admin = User(
        name="Super Admin",
        email="kovendhan.s3@gmail.com",
        password_hash=get_password_hash("password"),
        role="ADMIN",
        showroom_id=None,
    )

    db.add(admin)
    db.commit()

    print("✅ Admin + Showrooms seeded")


if __name__ == "__main__":
    seed()
