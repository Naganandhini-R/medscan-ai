import random
import uuid
import sys
from app.db.session import SessionLocal
from app.models.scan import Scan
from app.models.report import IssueReport

db = SessionLocal()

print("Fetching existing FAKE scans...")
fake_scans = db.query(Scan).filter(Scan.status == 'FAKE').all()

if not fake_scans:
    print("No FAKE scans found. Please generate scans first.")
    sys.exit(1)

issue_types = [
    "Counterfeit Suspected", 
    "Packaging Tampered", 
    "Missing Hologram", 
    "Batch ID Mismatch", 
    "Quality Issue"
]

report_descriptions = [
    "The packaging looked suspicious and didn't match the original brand colors. Please verify.",
    "The batch ID on the medicine strip didn't match the one on the outer box.",
    "There was no holographic seal on the medicine package as expected.",
    "The pills looked discolored and the font on the blister pack was blurry.",
    "System flagged this scan as high-risk FAKE. User confirmed the packaging is tampered.",
    "Pharmacist suspected this batch might be part of a recalled or counterfeit circulation.",
    "The QR code label was peeling off and appeared to be printed on a normal inkjet printer.",
    "User reported adverse effects. Upon checking, the medicine box lacked standard security features."
]

reports_added = 0
for i in range(20):
    # Pick a random fake scan to attach this report to
    scan = random.choice(fake_scans)
    
    # Add a tiny bit of jitter to the location to make it look like a new report in the same general area
    try:
        lat = str(float(scan.lat) + random.uniform(-0.01, 0.01)) if scan.lat else None
        lng = str(float(scan.lng) + random.uniform(-0.01, 0.01)) if scan.lng else None
    except:
        lat, lng = scan.lat, scan.lng

    report = IssueReport(
        id=str(uuid.uuid4()),
        scan_id=scan.id,
        medicine_name=scan.medicine_name,
        batch_id=scan.batch_id,
        manufacturer=scan.manufacturer,
        issue_type=random.choice(issue_types),
        location_details="User Reported via MedScan App",
        description=random.choice(report_descriptions),
        lat=lat,
        lng=lng
    )
    db.add(report)
    reports_added += 1

db.commit()
print(f"Successfully added {reports_added} new issue reports to the database based on existing FAKE scans.")
db.close()
