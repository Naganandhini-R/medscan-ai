import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv("c:/Users/HP/OneDrive/Desktop/medscan-ai/.env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        res = conn.execute(text("SELECT count(*) FROM manufacturers;"))
        count = res.fetchone()[0]
        print(f"Count: {count}")

        res = conn.execute(text("SELECT * FROM manufacturers LIMIT 1;"))
        row = res.fetchone()
        print(f"One row: {row}")
    except Exception as e:
        print(f"Error: {e}")
