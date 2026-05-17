from app.db.session import SessionLocal
from app.models.medicine import Medicine

db = SessionLocal()

print("Populating rich metadata for all medicines in the database...")

# Rich pharmaceutical metadata definitions mapped by keyword / brand
med_profiles = {
    "LIPITOR": {
        "salt": "Atorvastatin Calcium 10mg / 20mg",
        "dosage": "1 tablet daily, preferably in the evening or as prescribed.",
        "usage": "Used to lower blood cholesterol levels and reduce risk of heart disease.",
        "side_effects": "Muscle pain, mild nausea, headache, or digestive upset.",
        "storage": "Store below 25°C in a dry place. Protect from moisture.",
        "interactions": "Avoid grapefruit juice. Inform doctor if taking clarithromycin or itraconazole."
    },
    "LYRICA": {
        "salt": "Pregabalin 75mg / 150mg",
        "dosage": "1 capsule twice or thrice daily as directed by physician.",
        "usage": "Indicated for neuropathic pain, fibromyalgia, and adjunct therapy for seizures.",
        "side_effects": "Dizziness, somnolence, dry mouth, or peripheral edema.",
        "storage": "Store at room temperature (15°C to 30°C). Keep container tightly closed.",
        "interactions": "May enhance the sedative effects of alcohol, lorazepam, or opioids."
    },
    "ENBREL": {
        "salt": "Etanercept 50mg Injection",
        "dosage": "50mg injected subcutaneously once weekly.",
        "usage": "Used for moderate to severe rheumatoid arthritis, psoriatic arthritis, and plaque psoriasis.",
        "side_effects": "Injection site reactions, upper respiratory infections, or headache.",
        "storage": "Refrigerate at 2°C to 8°C (36°F to 46°F). Do not freeze.",
        "interactions": "Do not use concurrently with live vaccines or anakinra."
    },
    "NEULASTA": {
        "salt": "Pegfilgrastim 6mg/0.6mL Injection",
        "dosage": "6mg administered subcutaneously once per chemotherapy cycle.",
        "usage": "Stimulates white blood cell production to prevent neutropenia during chemotherapy.",
        "side_effects": "Bone pain, arthralgia, muscle pain, or fatigue.",
        "storage": "Store in refrigerator at 2°C to 8°C. Keep in outer carton to protect from light.",
        "interactions": "Concurrent use with lithium may potentiate the release of neutrophils."
    },
    "VEKLURY": {
        "salt": "Remdesivir 100mg for Injection",
        "dosage": "200mg loading dose on Day 1, followed by 100mg daily intravenous infusion.",
        "usage": "Antiviral medication indicated for the treatment of COVID-19 in hospitalized patients.",
        "side_effects": "Nausea, elevated transaminases, or hypersensitivity reactions.",
        "storage": "Store intact vials below 25°C. Reconstituted solution must be used promptly.",
        "interactions": "Co-administration with chloroquine or hydroxychloroquine is not recommended."
    },
    "TRUVADA": {
        "salt": "Emtricitabine 200mg + Tenofovir Disoproxil Fumarate 300mg",
        "dosage": "1 tablet daily taken orally with or without food.",
        "usage": "Used for HIV-1 treatment in combination with other antiretrovirals and for PrEP.",
        "side_effects": "Diarrhea, nausea, fatigue, headache, or dizziness.",
        "storage": "Store at 25°C (77°F); excursions permitted to 15°C–30°C.",
        "interactions": "Avoid concurrent use with nephrotoxic drugs like high-dose NSAIDs."
    },
    "SPIKEVAX": {
        "salt": "COVID-19 mRNA Vaccine (Nucleoside Modified)",
        "dosage": "0.5mL intramuscular injection as primary series or booster.",
        "usage": "Active immunization to prevent coronavirus disease 2019 (COVID-19).",
        "side_effects": "Pain at injection site, fatigue, myalgia, chills, or low-grade fever.",
        "storage": "Store frozen between -50°C and -15°C. Protect from light.",
        "interactions": "Allow at least 14 days before or after administration of other vaccines."
    },
    "DUPIXENT": {
        "salt": "Dupilumab 300mg/2mL Injection",
        "dosage": "600mg initial dose, followed by 300mg every other week subcutaneously.",
        "usage": "Indicated for moderate-to-severe atopic dermatitis, asthma, and chronic rhinosinusitis.",
        "side_effects": "Injection site reactions, conjunctivitis, or oral herpes.",
        "storage": "Refrigerate at 2°C to 8°C. Can be stored at room temperature up to 14 days.",
        "interactions": "Avoid use with live vaccines during treatment."
    },
    "VIAGRA": {
        "salt": "Sildenafil Citrate 50mg / 100mg",
        "dosage": "1 tablet taken 30 to 60 minutes before required activity. Max once daily.",
        "usage": "Indicated for the treatment of erectile dysfunction in men.",
        "side_effects": "Headache, flushing, dyspepsia, abnormal vision, or nasal congestion.",
        "storage": "Store at room temperature between 15°C and 30°C.",
        "interactions": "Strictly contraindicated with organic nitrates or riociguat (causes severe hypotension)."
    },
    "EPIPEN": {
        "salt": "Epinephrine 0.3mg Auto-Injector",
        "dosage": "0.3mg injected intramuscularly into the anterolateral aspect of the thigh.",
        "usage": "Emergency treatment of severe allergic reactions (anaphylaxis).",
        "side_effects": "Palpitations, sweating, anxiety, tremor, or headache.",
        "storage": "Store at 20°C to 25°C. Do not refrigerate. Protect from light.",
        "interactions": "Use with caution in patients taking cardiac glycosides or tricyclic antidepressants."
    },
    "HUMIRA": {
        "salt": "Adalimumab 40mg/0.4mL Injection",
        "dosage": "40mg administered subcutaneously every other week.",
        "usage": "Treats inflammatory conditions like rheumatoid arthritis, Crohn's disease, and psoriasis.",
        "side_effects": "Injection site pain, upper respiratory infections, or sinusitis.",
        "storage": "Refrigerate at 2°C to 8°C. Do not freeze. Protect from light.",
        "interactions": "Concurrent administration with live vaccines or abatacept is contraindicated."
    },
    "ELIQUIS": {
        "salt": "Apixaban 2.5mg / 5mg",
        "dosage": "5mg twice daily orally with or without food.",
        "usage": "Anticoagulant used to prevent stroke and blood clots in atrial fibrillation.",
        "side_effects": "Increased risk of bleeding, epistaxis, contusion, or hematuria.",
        "storage": "Store at 20°C to 25°C (68°F to 77°F).",
        "interactions": "Increased bleeding risk with NSAIDs, aspirin, warfarin, or SSRIs."
    },
    "DOLO": {
        "salt": "Paracetamol 650mg Tablets",
        "dosage": "1 tablet every 6 to 8 hours as needed for fever or pain. Max 4 tablets/day.",
        "usage": "Antipyretic and analgesic for symptomatic relief of fever and body ache.",
        "side_effects": "Rarely skin rashes or gastric irritation. Overdose causes hepatic injury.",
        "storage": "Store in a cool, dry place protected from direct sunlight.",
        "interactions": "Avoid chronic alcohol intake while taking high doses of paracetamol."
    },
    "VOLINI": {
        "salt": "Diclofenac Diethylamine 1.16% w/w Gel",
        "dosage": "Gently massage a small amount over the affected area 3 to 4 times daily.",
        "usage": "Topical anti-inflammatory gel for instant relief from joint pain, sprains, and backache.",
        "side_effects": "Occasional local skin irritation, redness, or allergic rash.",
        "storage": "Store below 30°C. Do not freeze. Replace cap tightly after use.",
        "interactions": "Minimal systemic absorption; highly safe when used as directed."
    },
    "OMEZ": {
        "salt": "Omeprazole 20mg Enteric Coated Capsules",
        "dosage": "1 capsule daily before breakfast for 14 to 28 days.",
        "usage": "Proton pump inhibitor used for peptic ulcers, GERD, and hyperacidity.",
        "side_effects": "Headache, abdominal pain, flatulence, or mild diarrhea.",
        "storage": "Store below 25°C in a dry place, protected from direct light.",
        "interactions": "Can delay the elimination of diazepam, phenytoin, or warfarin."
    },
    "NISE": {
        "salt": "Nimesulide 100mg Tablets",
        "dosage": "1 tablet twice daily after meals. Intended for short-term acute pain.",
        "usage": "Non-steroidal anti-inflammatory drug (NSAID) for acute inflammatory pain.",
        "side_effects": "Gastric discomfort, heartburn, nausea, or rare hepatic enzyme elevation.",
        "storage": "Store in a cool, dry place. Keep out of reach of children.",
        "interactions": "Avoid co-administration with other NSAIDs or anticoagulants."
    },
    "CALPOL": {
        "salt": "Paracetamol 500mg Tablets",
        "dosage": "1 tablet every 4 to 6 hours for headache or fever relief.",
        "usage": "Effective pain reliever and fever reducer.",
        "side_effects": "Extremely safe at recommended doses. Avoid overdose.",
        "storage": "Store at room temperature away from moisture and heat.",
        "interactions": "Check other cold/flu remedies to ensure they don't also contain paracetamol."
    },
    "AZITHRAL": {
        "salt": "Azithromycin 500mg Tablets",
        "dosage": "1 tablet daily for 3 to 5 days, taken 1 hour before or 2 hours after meals.",
        "usage": "Macrolide antibiotic used to treat various bacterial infections (respiratory, ear, skin).",
        "side_effects": "Diarrhea, nausea, abdominal pain, or mild vomiting.",
        "storage": "Store below 30°C in a dry place.",
        "interactions": "Antacids containing magnesium or aluminum can reduce absorption."
    },
    "PAN-D": {
        "salt": "Pantoprazole 40mg + Domperidone 30mg SR Capsules",
        "dosage": "1 capsule daily on an empty stomach, 30 minutes before breakfast.",
        "usage": "Used for gastroesophageal reflux disease (GERD) and dyspepsia with nausea.",
        "side_effects": "Dry mouth, headache, flatulence, or mild dizziness.",
        "storage": "Store in a cool, dry place away from direct sunlight.",
        "interactions": "May alter the absorption of pH-dependent drugs like ketoconazole."
    },
    "ROSUVAS": {
        "salt": "Rosuvastatin Calcium 10mg Tablets",
        "dosage": "1 tablet daily at any time of day, with or without food.",
        "usage": "Lowers bad cholesterol (LDL) and triglycerides in the blood.",
        "side_effects": "Myalgia, asthenia, headache, or mild constipation.",
        "storage": "Store below 30°C. Protect from moisture.",
        "interactions": "Increased risk of myopathy when co-administered with cyclosporine or gemfibrozil."
    },
    "AUGMENTIN": {
        "salt": "Amoxicillin 500mg + Potassium Clavulanate 125mg Tablets",
        "dosage": "1 tablet twice daily with meals for 5 to 7 days.",
        "usage": "Broad-spectrum antibiotic used for respiratory, genitourinary, and skin infections.",
        "side_effects": "Diarrhea, nausea, vomiting, or rare allergic skin rash.",
        "storage": "Store below 25°C in original moisture-proof packaging.",
        "interactions": "Probenecid decreases renal tubular secretion of amoxicillin."
    }
}

# Fallback generic profile
generic_profile = {
    "salt": "Premium Pharmaceutical Compound Formulation",
    "dosage": "1 tablet/capsule twice daily as directed by registered medical practitioner.",
    "usage": "Indicated for therapeutic management of diagnosed clinical conditions.",
    "side_effects": "Occasional mild gastrointestinal discomfort, dizziness, or fatigue.",
    "storage": "Store in a cool, dry place below 25°C. Protect from direct sunlight and moisture.",
    "interactions": "Consult healthcare provider before combining with over-the-counter supplements or antacids."
}

medicines = db.query(Medicine).all()
updated_count = 0

for m in medicines:
    med_name = m.name.upper() if m.name else ""
    
    # Match keyword
    matched = False
    for kw, profile in med_profiles.items():
        if kw in med_name:
            m.salt = profile["salt"]
            m.dosage = profile["dosage"]
            m.usage = profile["usage"]
            m.side_effects = profile["side_effects"]
            m.storage = profile["storage"]
            m.interactions = profile["interactions"]
            matched = True
            break
            
    if not matched:
        m.salt = generic_profile["salt"]
        m.dosage = generic_profile["dosage"]
        m.usage = generic_profile["usage"]
        m.side_effects = generic_profile["side_effects"]
        m.storage = generic_profile["storage"]
        m.interactions = generic_profile["interactions"]
        
    updated_count += 1

db.commit()
print(f"Successfully populated rich metadata for all {updated_count} medicines!")
db.close()
