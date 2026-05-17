import random
import uuid
import sys
from datetime import datetime
from app.db.session import SessionLocal
from app.models.scan import Scan
from app.models.report import IssueReport
from app.tasks.seed_data import medicines, companies
import json

db = SessionLocal()

print("Seeding 68 Extra Scans and 20 Extra Issue Reports...")

def get_random_location(region):
    if 'US' in region or 'NORTH AMERICA' in region or 'UNITED STATES' in region:
        return random.uniform(30.0, 45.0), random.uniform(-120.0, -75.0)
    elif 'DOMESTIC' in region or 'SOUTH ASIA' in region or 'INDIA' in region:
        return random.uniform(10.0, 30.0), random.uniform(70.0, 90.0)
    elif 'EUROPE' in region:
        return random.uniform(40.0, 60.0), random.uniform(-10.0, 30.0)
    elif 'LATIN AMERICA' in region:
        return random.uniform(-30.0, 10.0), random.uniform(-80.0, -40.0)
    elif 'EAST ASIA' in region:
        return random.uniform(20.0, 40.0), random.uniform(100.0, 130.0)
    else:
        return random.uniform(-50.0, 50.0), random.uniform(-120.0, 120.0)

# 1. Add 68 Scans
scans_added = []
for i in range(68):
    med = random.choice(medicines)
    lat, lng = get_random_location(med['region'])
    
    # 70% genuine, 20% fake, 10% suspicious
    rand_status = random.random()
    if rand_status < 0.7:
        status = "GENUINE"
        score = random.uniform(0.9, 1.0)
        bc_valid = True
    elif rand_status < 0.9:
        status = "FAKE"
        score = random.uniform(0.1, 0.4)
        bc_valid = False
    else:
        status = "SUSPICIOUS"
        score = random.uniform(0.4, 0.8)
        bc_valid = random.choice([True, False])
        
    scan_id = str(uuid.uuid4())
    scan = Scan(
        id=scan_id,
        score=score,
        status=status,
        blockchain_valid=bc_valid,
        medicine_name=med['medicine_name'],
        batch_id=med['batch_id'],
        expiry=med['exp_date'],
        manufacturer=med['manufacturer'],
        data={"confidence": score, "tamper_detected": status == "FAKE"},
        lat=lat,
        lng=lng,
        user_id=f"user_{random.randint(100, 999)}"
    )
    db.add(scan)
    scans_added.append(scan)

db.commit()
print("Added 68 scans.")

# 2. Add 20 Issue Reports
# Filter scans that are FAKE or SUSPICIOUS to attach reports to
bad_scans = [s for s in scans_added if s.status in ("FAKE", "SUSPICIOUS")]

# If we don't have enough bad scans, just use any scan
while len(bad_scans) < 20:
    bad_scans.append(random.choice(scans_added))

issue_types = ["Counterfeit Suspected", "Packaging Tampered", "Expired Medicine", "Quality Issue"]

for i in range(20):
    scan = bad_scans[i]
    report = IssueReport(
        id=str(uuid.uuid4()),
        scan_id=scan.id,
        medicine_name=scan.medicine_name,
        batch_id=scan.batch_id,
        manufacturer=scan.manufacturer,
        issue_type=random.choice(issue_types) if scan.status == "SUSPICIOUS" else "Counterfeit Suspected",
        location_details="User Reported Location",
        description=f"User reported a problem with {scan.medicine_name}. System flag: {scan.status}.",
        lat=str(scan.lat),
        lng=str(scan.lng)
    )
    db.add(report)

db.commit()
print("Added 20 issue reports.")
db.close()
