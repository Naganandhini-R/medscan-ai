import json
import os
from app.db.session import SessionLocal, engine, Base
from app.models.medicine import Medicine

def seed_medicines():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Path to external seed data
    seed_file = "backend/data/seed_medicines.json"

    if not os.path.exists(seed_file):
        print(f" No seed data found at {seed_file}. Skipping database seeding.")
        db.close()
        return

    try:
        with open(seed_file, "r") as f:
            initial_data = json.load(f)

        for data in initial_data:
            # Check if already exists
            exists = db.query(Medicine).filter(Medicine.name == data["name"]).first()
            if not exists:
                med = Medicine(**data)
                db.add(med)
                print(f"Added {data['name']} to database")

        db.commit()
        print(" Seed complete")
    except Exception as e:
        print(f"Error during seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_medicines()
