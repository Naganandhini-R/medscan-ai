import sys
import os
import random
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.report import IssueReport
from app.models.scan import Scan

def seed_reports():
    db = SessionLocal()
    print("Seeding Issue Reports...")

    # Fetch some fake scans to link reports to
    fake_scans = db.query(Scan).filter(Scan.status == "FAKE").limit(5).all()
    
    if not fake_scans:
        print("No FAKE scans found. Fetching any scan...")
        fake_scans = db.query(Scan).limit(5).all()
        
    issue_types = [
        "Counterfeit Suspected",
        "Expired Medicine Sold",
        "Packaging Tampered",
        "No Hologram Present"
    ]
    
    shop_locations = [
        "Apollo Pharmacy, Anna Nagar",
        "MedPlus, T Nagar",
        "Local Medical Shop, Velachery",
        "Unknown street vendor, Guindy"
    ]
    
    count = 0
    for scan in fake_scans:
        report = IssueReport(
            scan_id=scan.id,
            medicine_name=scan.medicine_name,
            batch_id=scan.batch_id,
            manufacturer=scan.manufacturer,
            issue_type=random.choice(issue_types),
            location_details=random.choice(shop_locations),
            description="The packaging looked very suspicious and the color was off. I scanned it and it said fake.",
            lat=str(scan.lat) if scan.lat else "13.0827",
            lng=str(scan.lng) if scan.lng else "80.2707",
            created_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
        )
        db.add(report)
        count += 1
        
    db.commit()
    print(f" Seeded {count} Issue Reports successfully!")
    db.close()

if __name__ == "__main__":
    seed_reports()
