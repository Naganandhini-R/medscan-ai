import sys
import os
import csv

from dotenv import load_dotenv

# Add the backend directory to sys.path so we can import app modules
# Assuming this script is running from medscan-ai root or backend/scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # Go up to backend
project_root = os.path.dirname(backend_dir)  # Go up to medscan-ai

sys.path.append(backend_dir)

# Load environment variables explicitly if .env exists
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

from app.db.session import SessionLocal
from app.models.drug import BannedDrug


def seed_banned_drugs():
    db = SessionLocal()

    # Try multiple paths for CSV
    paths_to_try = [
        os.path.join(backend_dir, "data", "csv", "prohibited_fdc_clean.csv"),
        "prohibited_fdc_clean.csv",  # In case running from same dir
        "/app/prohibited_fdc_clean.csv",
    ]

    csv_path = None
    for p in paths_to_try:
        if os.path.exists(p):
            csv_path = p
            break

    if not csv_path:
        print(f" Error: CSV file not found. Checked: {paths_to_try}")
        return

    print(f"🔄 Reading Banned Drugs from {csv_path}...")

    try:
        count = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            # Use DictReader for handling the CSV structure
            reader = csv.DictReader(f)

            # Normalize headers (strip whitespace and lower case)
            if reader.fieldnames:
                reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

            # Identify relevant columns
            # Expected: s._no., drugs_name, notification_no.__&_date
            drug_col = next(
                (c for c in reader.fieldnames if "drug" in c or "name" in c), None
            )
            notif_col = next(
                (c for c in reader.fieldnames if "notification" in c or "date" in c),
                None,
            )

            if not drug_col:
                print(" Error: Could not identify Drug Name column in CSV.")
                print(f"Found columns: {reader.fieldnames}")
                return

            for row in reader:
                # Get values and clean them
                if not row[drug_col]:
                    continue

                drug_name = row[drug_col].strip().replace("\n", " ")
                notification = (
                    row[notif_col].strip().replace("\n", " ")
                    if notif_col and row[notif_col]
                    else "Unknown"
                )

                # Check if exists
                existing = (
                    db.query(BannedDrug).filter(BannedDrug.salt == drug_name).first()
                )
                if not existing:
                    new_drug = BannedDrug(
                        brand="Generic FDC",  # These are usually defining the composition
                        salt=drug_name,
                        category="BANNED",
                        source=notification,
                        reason="Prohibited Fixed Dose Combination (FDC)",
                    )
                    db.add(new_drug)
                    count += 1

        db.commit()
        print(f"Successfully added {count} banned drugs to the database.")

    except Exception as e:
        print(f" Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_banned_drugs()
