import pandas as pd
import os
import sys
import re
import glob
from dotenv import load_dotenv

# Load env before anything else
load_dotenv()

# Add backend to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine, Base
from app.models.drug import BannedDrug
from app.models.user import User
from app.models.scan import Scan

# Ensure table exists
Base.metadata.create_all(bind=engine)

CSV_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "csv"
)


def clean_value(val):
    if pd.isna(val) or val == "":
        return None
    val = str(val).strip()
    # Remove numbering like "1. ", "10. ", "95. 3#"
    val = re.sub(r"^\d+\.?\s*(?:\d+#)?\s*", "", val)
    # Remove leading/trailing quotes and newlines
    val = val.replace("\n", " ").strip()
    return val


def seed_data():
    db = SessionLocal()
    try:
        # Clear existing data to avoid duplicates
        db.query(BannedDrug).delete()
        print(" Cleared existing banned drugs table.")

        # Find all cleaned CSV files
        cleaned_files = glob.glob(os.path.join(CSV_DIR, "cleaned_*.csv"))
        print(f" Found {len(cleaned_files)} cleaned CSV files for seeding.")

        total_added = 0
        for file_path in cleaned_files:
            file_name = os.path.basename(file_path)
            print(f" Seeding from {file_name}...")

            try:
                df = pd.read_csv(file_path)
                df.columns = [c.lower().strip() for c in df.columns]

                # Identify columns dynamically
                salt_col = None
                for col in [
                    "salt",
                    "drugs_name",
                    "drug_name",
                    "name_of_the_fdc",
                    "composition",
                ]:
                    if col in df.columns:
                        salt_col = col
                        break

                if not salt_col:
                    # Fallback: look for a column that has "drug" or "composition" in it
                    for col in df.columns:
                        if "drug" in col or "composition" in col or "name" in col:
                            salt_col = col
                            break

                if not salt_col:
                    print(
                        f" Could not find salt/drug column in {file_name}, columns: {df.columns.tolist()}"
                    )
                    continue

                # Reason/Notification column
                reason_col = None
                for col in [
                    "notification",
                    "notification_no.__&_date",
                    "notification_no_&_date",
                    "reason",
                ]:
                    if col in df.columns:
                        reason_col = col
                        break

                # Determine category based on filename
                category = "Banned/Prohibited"
                if "restricted" in file_name.lower():
                    category = "Restricted"
                elif "prohibited" in file_name.lower() or "banned" in file_name.lower():
                    category = "Prohibited"
                elif "permitted" in file_name.lower():
                    category = "Permitted (Subsequent List)"

                count = 0
                for _, row in df.iterrows():
                    salt = clean_value(row.get(salt_col))
                    if salt and len(salt) > 3:
                        reason_val = (
                            clean_value(row.get(reason_col)) if reason_col else None
                        )

                        drug = BannedDrug(
                            salt=salt,
                            category=category,
                            source=file_name.replace("cleaned_", "").replace(
                                ".csv", ""
                            ),
                            reason=(
                                f"Notification: {reason_val}"
                                if reason_val
                                else "Listed in regulations"
                            ),
                        )
                        db.add(drug)
                        count += 1

                print(f"Added {count} entries from {file_name}.")
                total_added += count
            except Exception as e:
                print(f" Error processing {file_name}: {e}")

        db.commit()
        print(f"\n Database seeding complete! Total entries: {total_added}")
    except Exception as e:
        print(f" Critical error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
