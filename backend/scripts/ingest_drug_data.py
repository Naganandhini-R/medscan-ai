import csv
import os
import glob
from sqlalchemy import create_engine, text

# Database connection
DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:Nandhu2004@postgres:5432/medscan"
)
engine = create_engine(DB_URL)

CSV_DIR = "/app/data_csv"


def load_csvs():
    csv_files = glob.glob(os.path.join(CSV_DIR, "cleaned_*.csv"))

    total_loaded = 0

    with engine.connect() as conn:
        for file in csv_files:
            print(f"Processing {os.path.basename(file)}...")
            with open(file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows_to_insert = []

                for row in reader:
                    brand = row.get("brand") or row.get("drug_name")
                    salt = row.get("salt") or row.get("composition") or row.get("fdc")
                    source = os.path.basename(file)

                    if "prohibited" in file.lower() or "banned" in file.lower():
                        category = "BANNED"
                    elif "restricted" in file.lower():
                        category = "RESTRICTED"
                    else:
                        category = "SAFETY_LIST"

                    rows_to_insert.append(
                        {
                            "brand": brand,
                            "salt": salt,
                            "category": category,
                            "source": source,
                            "reason": "",
                        }
                    )

                if rows_to_insert:
                    query = text("""
                        INSERT INTO banned_drugs (brand, salt, category, source, reason)
                        VALUES (:brand, :salt, :category, :source, :reason)
                    """)
                    conn.execute(query, rows_to_insert)
                    conn.commit()
                    total_loaded += len(rows_to_insert)
                    print(f"Loaded {len(rows_to_insert)} rows.")

    print(f"Finished. Total loaded: {total_loaded}")


if __name__ == "__main__":
    load_csvs()
