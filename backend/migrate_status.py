import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Path to .env (Project Root)
load_dotenv("c:/Users/HP/OneDrive/Desktop/medscan-ai/.env")

# Construct URL or get from env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_pass = os.getenv("POSTGRES_PASSWORD", "password")
    db_host = os.getenv("POSTGRES_SERVER", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "medscan")
    DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

print(f"DEBUG: Connecting to {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("DEBUG: Connection successful. Checking if column exists...")
        # Check if column exists first
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='manufacturers' AND column_name='status';"
            )
        )
        exists = result.fetchone()

        if not exists:
            print("Action: Adding 'status' column...")
            conn.execute(
                text(
                    "ALTER TABLE manufacturers ADD COLUMN status VARCHAR DEFAULT 'PENDING' NOT NULL;"
                )
            )
            conn.commit()
            print("SUCCESS: Column added.")
        else:
            print("INFO: Column already exists.")
except Exception as e:
    print(f"FATAL ERROR: {str(e)}")
    import traceback

    traceback.print_exc()
