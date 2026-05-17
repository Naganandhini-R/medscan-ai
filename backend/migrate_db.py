from app.db.session import engine
from sqlalchemy import text
import traceback


def migrate():
    try:
        with engine.connect() as conn:
            columns = [
                ("lat", "FLOAT"),
                ("lng", "FLOAT"),
                ("user_id", "VARCHAR"),
                ("data", "JSON"),
                ("expiry", "VARCHAR"),
                ("manufacturer", "VARCHAR"),
                ("medicine_name", "VARCHAR"),
                ("batch_id", "VARCHAR"),
                ("blockchain_valid", "BOOLEAN"),
            ]
            for col, col_type in columns:
                query = text(
                    f"SELECT column_name FROM information_schema.columns WHERE table_name='scans' AND column_name='{col}';"
                )
                res = conn.execute(query).fetchone()
                if not res:
                    print(f"Adding {col} to scans...")
                    conn.execute(
                        text(f"ALTER TABLE scans ADD COLUMN {col} {col_type};")
                    )
            conn.commit()
        print("DB Migration successful")
    except Exception as e:
        traceback.print_exc()


if __name__ == "__main__":
    migrate()
