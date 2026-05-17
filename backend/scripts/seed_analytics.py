import os
import random
from datetime import datetime, timedelta
from app.db.session import SessionLocal, engine
from app.models.scan import Scan
from app.models.manufacturer import Manufacturer
from app.models.medicine import Medicine


def seed_realtime_data():
    db = SessionLocal()
    print(" Commencing Real-Time Data Injection from Database Registry...")

    # Fetch real data from the database instead of hardcoding strings
    existing_manufacturers = db.query(Manufacturer).all()
    existing_medicines = db.query(Medicine).all()

    if not existing_manufacturers or not existing_medicines:
        print(" Warning: No manufacturers or medicines found in database.")
        print("Please register a company and a batch first via the portal.")
        db.close()
        return

    mfg_names = [m.name for m in existing_manufacturers]
    med_names = [m.name for m in existing_medicines]

    # 2. Cities for Real-Time Mapping
    locations = [
        {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
        {"name": "Delhi", "lat": 28.6139, "lng": 77.2090},
        {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
        {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
        {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
        {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    ]

    # 3. Inject Genuine Scans (Dynamic from DB)
    print(f" Seeding scans for {len(med_names)} registered brands...")
    for _ in range(50):
        loc = random.choice(locations)
        target_med = random.choice(existing_medicines)

        lat = loc["lat"] + random.uniform(-0.5, 0.5)
        lng = loc["lng"] + random.uniform(-0.5, 0.5)

        scan = Scan(
            medicine_name=target_med.name,
            batch_id=f"BTCH-{random.randint(1000, 9999)}",
            manufacturer=target_med.manufacturer or random.choice(mfg_names),
            status="GENUINE",
            score=random.uniform(90, 99),
            lat=lat,
            lng=lng,
            created_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440)),
        )
        db.add(scan)

    # 4. Inject "Clone Attack" Outbreak (Cluster in Mumbai)
    # Picks a real medicine registered in your DB to simulate an attack
    attack_target = random.choice(existing_medicines)
    print(f" Injecting AI Outbreak Cluster for '{attack_target.name}' in Mumbai...")

    mumbai = locations[0]
    for _ in range(15):
        lat = mumbai["lat"] + random.uniform(-0.02, 0.02)
        lng = mumbai["lng"] + random.uniform(-0.02, 0.02)

        scan = Scan(
            medicine_name=attack_target.name,
            batch_id=f"CLONE-{random.randint(10, 99)}",
            manufacturer=attack_target.manufacturer or random.choice(mfg_names),
            status="FAKE",
            score=random.uniform(20, 45),
            lat=lat,
            lng=lng,
            created_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 120)),
        )
        db.add(scan)

    # 5. Inject Scattered Fakes (Delhi/Chennai)
    for loc in [locations[1], locations[2]]:
        scatter_target = random.choice(existing_medicines)
        for _ in range(3):
            scan = Scan(
                medicine_name=scatter_target.name,
                batch_id=f"FAKE-{random.randint(100, 999)}",
                manufacturer=scatter_target.manufacturer or random.choice(mfg_names),
                status="FAKE",
                score=random.uniform(10, 30),
                lat=loc["lat"] + random.uniform(-0.1, 0.1),
                lng=loc["lng"] + random.uniform(-0.1, 0.1),
            )
            db.add(scan)

    db.commit()
    print(" Real-Time Database Ecosystem Populated Using Registered Assets!")
    db.close()


if __name__ == "__main__":
    seed_realtime_data()
