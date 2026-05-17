import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.manufacturer import Manufacturer
from app.models.medicine import Medicine
from app.models.scan import Scan
from app.models.user import User

def seed_rubired():
    db = SessionLocal()
    
    # Get the user
    user = db.query(User).filter(User.email == "naganandhini2712@gmail.com").first()
    user_id = str(user.id) if user else "1"
    
    # Clean old scans of Rubired Z for this batch to avoid duplicates
    db.query(Scan).filter(Scan.medicine_name == "Rubired Z", Scan.batch_id == "GF244009").delete()
    db.commit()
    
    # 1. Add Manufacturer if missing
    mfg = db.query(Manufacturer).filter(Manufacturer.name == "MACLEODS PHARMACEUTICALS LTD.").first()
    if not mfg:
        mfg = Manufacturer(
            name="MACLEODS PHARMACEUTICALS LTD.",
            security_email="macleodssecurity@gmail.com",
            status="VERIFIED",
            email_verified=True
        )
        db.add(mfg)
        db.commit()
        db.refresh(mfg)
        print("MACLEODS manufacturer added.")
    
    # 2. Add Medicine if missing
    med = db.query(Medicine).filter(Medicine.name == "Rubired Z").first()
    if not med:
        med = Medicine(
            name="Rubired Z",
            manufacturer="MACLEODS PHARMACEUTICALS LTD.",
            salt="Ferrous Ascorbate, Folic Acid, Zinc Sulphate",
            dosage="1 capsule daily after a meal or as directed by the physician.",
            usage="Used for treatment of Iron deficiency anemia and nutritional deficiencies.",
            side_effects="Mild stomach upset, dark stools, or nausea.",
            storage="Store in a cool and dry place. Protect from direct light."
        )
        db.add(med)
        db.commit()
        db.refresh(med)
        print("Rubired Z medicine added.")
        
    # 3. Add Scan History Entry (Genuine Scanned Record with Blockchain Valid, Expiry, Salts, Verification Source)
    scan_genuine = Scan(
        medicine_name="Rubired Z",
        batch_id="GF244009",
        expiry="2026-06-30", 
        manufacturer="MACLEODS PHARMACEUTICALS LTD.",
        status="GENUINE",
        score=99.2,
        blockchain_valid=True, # MUST BE TRUE AS IT IS REGISTERED ON THE BLOCKCHAIN
        data={
            "verification_source": "Centralized Pharma Node",
            "salt": "Ferrous Ascorbate, Folic Acid, Zinc Sulphate",
            "dosage": "1 capsule daily after a meal or as directed by the physician.",
            "usage": "Used for treatment of Iron deficiency anemia and nutritional deficiencies.",
            "side_effects": "Mild stomach upset, dark stools, or nausea.",
            "storage": "Store in a cool and dry place. Protect from direct light.",
            "interactions": "Do not take with antacids or dairy products for 2 hours."
        },
        user_id=user_id,
        lat=13.0827,
        lng=80.2707
    )
    
    db.add(scan_genuine)
    db.commit()
    print("Genuine Scan for Rubired Z added successfully with expiry date, blockchain_valid=True, salts, and verification_source!")
    
    db.close()

if __name__ == "__main__":
    seed_rubired()
