import sys
import os
from dotenv import load_dotenv, find_dotenv

# Add the parent directory to sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load env
load_dotenv(find_dotenv())

from app.db.session import SessionLocal
from app.models.medicine import Medicine

def main():
    db = SessionLocal()
    try:
        medicines = db.query(Medicine).all()
        
        if not medicines:
            print("📭 No extra clinical data found in the local database.")
            return

        print(f"🏥 --- MedScan-AI FULL CLINICAL STORAGE (DATABASE) --- 🏥")
        print(f"Total Records: {len(medicines)}\n")

        for med in medicines:
            print(f" Medicine Name:  {med.name}")
            print(f"   Salt/Comp:   {med.salt}")
            print(f"   Dosage:      {med.dosage}")
            print(f"    Side Effects: {med.side_effects}")
            print(f"    Storage:      {med.storage}")
            print(f"   Manufacturer: {med.manufacturer}")
            print("-" * 60)

    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
