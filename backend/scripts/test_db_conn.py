import os
import sys
from dotenv import load_dotenv

# Load root .env
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

print("--- DEBUG DB CONFIG ---")
print(f"POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
print(f"POSTGRES_PORT: {settings.POSTGRES_PORT}")
print(f"POSTGRES_USER: {settings.POSTGRES_USER}")
print(f"POSTGRES_DB: {settings.POSTGRES_DB}")
print(
    f"DATABASE_URL: {settings.DATABASE_URL.replace(settings.POSTGRES_PASSWORD, '****')}"
)
print("-----------------------")

try:
    from sqlalchemy import create_engine

    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print(" Successfully connected to the database!")
except Exception as e:
    print(f" Connection failed: {e}")
