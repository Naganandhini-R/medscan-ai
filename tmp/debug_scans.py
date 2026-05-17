import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'backend')))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.scan import Scan

db_url = "postgresql://postgres:Nandhu2004@127.0.0.1:5433/medscan"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
db = Session()

try:
    scans = db.query(Scan.id, Scan.medicine_name, Scan.manufacturer, Scan.status).all()
    print("Scan Details (Manufacturer focus):")
    for s in scans:
        print(f"- ID: {s.id[:8]}... | Med: {s.medicine_name} | Mfr: '{s.manufacturer}' | Status: {s.status}")
finally:
    db.close()
