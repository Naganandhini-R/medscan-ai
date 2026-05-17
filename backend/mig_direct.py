import psycopg2
import os
from dotenv import load_dotenv

load_dotenv("c:/Users/HP/OneDrive/Desktop/medscan-ai/.env")
url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    print("Connected!")
    cur.execute(
        "ALTER TABLE manufacturers ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'PENDING' NOT NULL;"
    )
    conn.commit()
    print("Success!")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
