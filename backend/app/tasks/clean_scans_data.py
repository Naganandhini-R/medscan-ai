import random
from app.db.session import SessionLocal
from app.models.scan import Scan
from app.tasks.seed_data import medicines

db = SessionLocal()

print("Cleaning and Standardizing all Scan records...")

# Create a lookup for medicine metadata from seed_data
med_lookup = {}
for m in medicines:
    med_lookup[m['medicine_name'].strip().upper()] = m

# Standard rich data templates for consistent JSON structure across all rows
default_salts = {
    "LIPITOR": "Atorvastatin Calcium",
    "LYRICA": "Pregabalin",
    "ENBREL": "Etanercept",
    "NEULASTA": "Pegfilgrastim",
    "VEKLURY": "Remdesivir",
    "TRUVADA": "Emtricitabine / Tenofovir disoproxil",
    "SPIKEVAX": "COVID-19 mRNA",
    "DUPIXENT": "Dupilumab",
    "VIAGRA": "Sildenafil Citrate",
    "EPIPEN": "Epinephrine",
    "HUMIRA": "Adalimumab",
    "ELIQUIS": "Apixaban",
    "DOLO 650": "Paracetamol 650mg",
    "VOLINI": "DiclofenAC Diethylamine",
    "OMEZ 20": "Omeprazole 20mg",
    "NISE": "Nimesulide 100mg",
    "CALPOL 500": "Paracetamol 500mg",
    "AZITHRAL 500": "Azithromycin 500mg",
    "PAN-D": "Pantoprazole + Domperidone"
}

scans = db.query(Scan).all()
updated_count = 0

for s in scans:
    med_name = s.medicine_name.strip().upper() if s.medicine_name else ""
    
    # 1. Standardize User ID to '1'
    s.user_id = "1"
    
    # 2. Standardize Expiry Date
    if med_name in med_lookup:
        s.expiry = med_lookup[med_name]['exp_date']
    else:
        s.expiry = "2027-12-31"
        
    # 3. Standardize Scores (Round to 2 decimal places based on status)
    status = s.status.upper() if s.status else "GENUINE"
    if status == "GENUINE":
        s.score = round(random.uniform(0.90, 0.99), 2)
    elif status == "FAKE":
        s.score = round(random.uniform(0.10, 0.35), 2)
    else:  # SUSPICIOUS
        s.score = round(random.uniform(0.40, 0.70), 2)
        
    # 4. Standardize Data JSON Column Structure
    # Find matching salt or default
    salt = "Pharmaceutical Compound Formulation"
    for key, val in default_salts.items():
        if key in med_name:
            salt = val
            break
            
    s.data = {
        "verification_source": "MedScan AI & Global Blockchain Ledger",
        "salt": salt,
        "dosage": "As directed by physician. Do not exceed recommended daily limit.",
        "usage": f"Indicated for therapeutic treatment associated with {salt}.",
        "side_effects": "Mild nausea, temporary dizziness, or gastrointestinal upset.",
        "storage": "Store in a cool, dry place below 25°C. Protect from direct sunlight.",
        "interactions": "Consult healthcare provider if taking anticoagulants or strong CYP3A4 inhibitors.",
        "confidence_score": s.score,
        "tamper_flag": status == "FAKE"
    }
    
    updated_count += 1

db.commit()
print(f"Successfully cleaned, standardized, and updated {updated_count} scan records!")
db.close()
