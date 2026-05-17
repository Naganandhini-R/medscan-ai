import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.manufacturer import Manufacturer
from app.models.medicine import Medicine
from app.models.scan import Scan
from app.models.user import User

def seed_megaferon():
    db = SessionLocal()
    
    # Get the user
    user = db.query(User).filter(User.email == "naganandhini2712@gmail.com").first()
    user_id = str(user.id) if user else "1"
    
    # Clean old scans of Megaferon for this batch to avoid duplicates
    db.query(Scan).filter(Scan.medicine_name == "Megaferon", Scan.batch_id == "INC2570").delete()
    db.commit()
    
    # 1. Add Manufacturer if missing
    mfg = db.query(Manufacturer).filter(Manufacturer.name == "Aristo Pharmaceuticals").first()
    if not mfg:
        mfg = Manufacturer(
            name="Aristo Pharmaceuticals",
            security_email="aristosecurity@gmail.com",
            status="VERIFIED",
            email_verified=True
        )
        db.add(mfg)
        db.commit()
        db.refresh(mfg)
        print("Aristo Pharmaceuticals manufacturer added.")
    
    # 2. Add Medicine if missing
    med = db.query(Medicine).filter(Medicine.name == "Megaferon").first()
    if not med:
        med = Medicine(
            name="Megaferon",
            manufacturer="Aristo Pharmaceuticals",
            salt="Iron Polymaltose Complex",
            dosage="5ml to 10ml daily for adults or as prescribed.",
            usage="Effective for quick restoration of iron levels in the body.",
            side_effects="Constipation or diarrhea (temporary).",
            storage="Store at room temperature. Keep bottle tightly closed."
        )
        db.add(med)
        db.commit()
        db.refresh(med)
        print("Megaferon medicine added.")
        
    # 3. Add Scan History Entry (Genuine Scanned Record with Blockchain Valid, Expiry, Salts, Verification Source)
    scan_genuine = Scan(
        medicine_name="Megaferon",
        batch_id="INC2570",
        expiry="2026-12-01", 
        manufacturer="Aristo Pharmaceuticals",
        status="GENUINE",
        score=98.9,
        blockchain_valid=True, # MUST BE TRUE AS IT IS REGISTERED ON THE BLOCKCHAIN
        data={
            "verification_source": "Centralized Pharma Node",
            "salt": "Iron Polymaltose Complex",
            "dosage": "5ml to 10ml daily for adults or as prescribed.",
            "usage": "Effective for quick restoration of iron levels in the body.",
            "side_effects": "Constipation or diarrhea (temporary).",
            "storage": "Store at room temperature. Keep bottle tightly closed.",
            "interactions": "Tell your doctor if you are taking antibiotics like Tetracycline."
        },
        user_id=user_id,
        lat=13.0827,
        lng=80.2707
    )
    
    db.add(scan_genuine)
    db.commit()
    print("Genuine Scan for Megaferon added successfully with expiry date, blockchain_valid=True, salts, and verification_source!")
    
    db.close()

if __name__ == "__main__":
    seed_megaferon()
