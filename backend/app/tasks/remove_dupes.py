from app.db.session import SessionLocal
from app.models.report import IssueReport

db = SessionLocal()
reports = db.query(IssueReport).order_by(IssueReport.created_at.desc()).all()

seen = set()
to_delete = []

for r in reports:
    # Use scan_id as key, or a composite key if preferred
    # To remove EXACT duplicates we might want to check the entire content, 
    # but removing duplicate reports per scan is safer to prevent multiple reports 
    # flooding one fake scan.
    key = r.scan_id
    if key in seen:
        to_delete.append(r.id)
    else:
        seen.add(key)

if to_delete:
    db.query(IssueReport).filter(IssueReport.id.in_(to_delete)).delete(synchronize_session=False)
    db.commit()
    print(f"Removed {len(to_delete)} duplicate issue reports.")
else:
    print("No duplicates found.")

db.close()
