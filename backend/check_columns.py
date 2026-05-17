import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv("c:/Users/HP/OneDrive/Desktop/medscan-ai/.env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

columns = inspector.get_columns("manufacturers")
print("Columns in 'manufacturers' table:")
for column in columns:
    print(f"- {column['name']}: {column['type']}")
