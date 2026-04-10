from sqlalchemy import create_engine

DATABASE_URL = "PASTE_YOUR_CONNECTION_STRING_HERE"

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("✅ CONNECTION SUCCESS")
    conn.close()
except Exception as e:
    print("❌ CONNECTION FAILED")
    print(e)