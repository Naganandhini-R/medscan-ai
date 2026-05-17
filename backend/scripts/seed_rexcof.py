import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.manufacturer import Manufacturer
from app.models.medicine import Medicine
from app.models.scan import Scan
from app.models.user import User

def seed_rexcof():
    db = SessionLocal()
    
    # Get the user
    user = db.query(User).filter(User.email == "naganandhini2712@gmail.com").first()
    user_id = str(user.id) if user else "1"
    
    # Clean old scans of Rexcof first to avoid duplicates
    db.query(Scan).filter(Scan.medicine_name == "Rexcof DX Cough Syrup").delete()
    db.commit()
    
    # 1. Add Manufacturer if missing
    mfg = db.query(Manufacturer).filter(Manufacturer.name == "Cipla Limited").first()
    if not mfg:
        mfg = Manufacturer(
            name="Cipla Limited",
            security_email="ciplasecurity@gmail.com",
            status="VERIFIED",
            email_verified=True
        )
        db.add(mfg)
        db.commit()
        db.refresh(mfg)
        print("Cipla Limited manufacturer added.")
    
    # 2. Add Medicine if missing
    med = db.query(Medicine).filter(Medicine.name == "Rexcof DX Cough Syrup").first()
    if not med:
        med = Medicine(
            name="Rexcof DX Cough Syrup",
            manufacturer="Cipla Limited",
            salt="Chlorpheniramine Maleate + Dextromethorphan Hydrobromide",
            dosage="10ml twice a day",
            usage="Dry Cough relief",
            side_effects="Sleepiness, dizziness",
            storage="Store below 30°C"
        )
        db.add(med)
        db.commit()
        db.refresh(med)
        print("Rexcof DX Cough Syrup medicine added.")
        
    # 3. Add Scans (Only Genuine as requested by user, with Expiry, Blockchain Valid, and Verification Source)
    scan_genuine = Scan(
        medicine_name="Rexcof DX Cough Syrup",
        batch_id="RXCF2603",
        expiry="2026-09-30", 
        manufacturer="Cipla Limited",
        status="GENUINE",
        score=98.6,
        blockchain_valid=True, # MUST BE TRUE AS IT IS REGISTERED ON THE BLOCKCHAIN
        data={
            "verification_source": "Centralized Pharma Node",
            "salt": "Chlorpheniramine Maleate + Dextromethorphan Hydrobromide",
            "usage": "Dry Cough relief",
            "side_effects": "Sleepiness, dizziness",
            "storage": "Store below 30°C"
        },
        user_id=user_id,
        lat=13.0827,
        lng=80.2707
    )
    
    db.add(scan_genuine)
    db.commit()
    print("Genuine Scan for Rexcof DX Cough Syrup added successfully with expiry date, blockchain_valid=True, and verification_source!")
    
    db.close()

if __name__ == "__main__":
    seed_rexcof()
