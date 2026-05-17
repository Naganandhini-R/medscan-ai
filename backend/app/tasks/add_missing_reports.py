import random
import uuid
import sys
from app.db.session import SessionLocal
from app.models.scan import Scan
from app.models.report import IssueReport
from app.tasks.seed_data import medicines, companies

db = SessionLocal()

def get_random_location():
    return random.uniform(-50.0, 50.0), random.uniform(-120.0, 120.0)

issue_types = [
    "Counterfeit Suspected", 
    "Packaging Tampered"
]

report_descriptions = [
    "The QR code label was peeling off and appeared to be printed on a normal inkjet printer.",
    "User reported adverse effects. Upon checking, the medicine box lacked standard security features."
]

scans_added = 0
for i in range(2):
    med = random.choice(medicines)
    lat, lng = get_random_location()
    
    status = "FAKE"
    score = random.uniform(0.1, 0.4)
    bc_valid = False
        
    scan = Scan(
        id=str(uuid.uuid4()),
        score=score,
        status=status,
        blockchain_valid=bc_valid,
        medicine_name=med['medicine_name'],
        batch_id=med['batch_id'],
        expiry=med['exp_date'],
        manufacturer=med['manufacturer'],
        data={"confidence": score, "tamper_detected": True},
        lat=lat,
        lng=lng,
        user_id=f"user_{random.randint(100, 999)}"
    )
    db.add(scan)
    db.flush() # flush to get the scan ready
    
    report = IssueReport(
        id=str(uuid.uuid4()),
        scan_id=scan.id,
        medicine_name=scan.medicine_name,
        batch_id=scan.batch_id,
        manufacturer=scan.manufacturer,
        issue_type=random.choice(issue_types),
        location_details="User Reported via App",
        description=random.choice(report_descriptions),
        lat=str(lat),
        lng=str(lng)
    )
    db.add(report)
    scans_added += 1

db.commit()
print(f"Successfully added {scans_added} new scans and issue reports. Total should now be 20.")
db.close()
