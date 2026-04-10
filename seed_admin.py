# seed_admin.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
from app.models.user import User

# Use the URL that we know works
DATABASE_URL = "mysql+pymysql://3TDtmcbjnmwrtwJ.root:ZvO8easP0hEgvu09@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/zhagaram_db"

engine = create_engine(DATABASE_URL, connect_args={"ssl": {"ssl_mode": "REQUIRED"}})
SessionLocal = sessionmaker(bind=engine)

def seed_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("Admin user already exists!")
            return

        admin_user = User(
            name="System Admin",
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"), # Change this later!
            role="ADMIN",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_user()