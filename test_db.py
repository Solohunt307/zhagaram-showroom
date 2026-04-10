from sqlalchemy import create_engine

DATABASE_URL = "DATABASE_URL=mysql+pymysql://3TDtmcbjnmwrtwJ.root:kq7m601QHJy8ONhE@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/zhagaram_db"

try:
    engine = create_engine(DATABASE_URL)
    conn = engine.connect()
    print("✅ CONNECTION SUCCESS")
    conn.close()
except Exception as e:
    print("❌ CONNECTION FAILED")
    print(e)
