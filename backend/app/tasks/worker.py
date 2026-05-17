from celery import Celery
import os
from app.db.session import SessionLocal
from app.models.scan import Scan
from app.blockchain.web3_client import verify_batch
from app.tasks.scan_pipeline import run_vision_pipeline
from app.models.drug import BannedDrug
from sqlalchemy import or_
from app.services.analytics_service import AnalyticsService
from app.services.email_service import send_outbreak_alert

celery = Celery(
    "medscan",
    broker="redis://redis:6379/0",  
    backend="redis://redis:6379/0",
)

def update_result(
    scan_id,
    score,
    status,
    blockchain_valid=False,
    lat=None,
    lng=None,
    batch_id=None,
    expiry=None,
    manufacturer=None,
    medicine_name=None,
    data=None,
):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            scan.score = score
            scan.status = status
            scan.blockchain_valid = blockchain_valid  # Pass boolean directly now
            scan.lat = lat
            scan.lng = lng
            scan.batch_id = batch_id
            scan.expiry = expiry
            scan.manufacturer = manufacturer
            scan.medicine_name = medicine_name
            scan.data = data
            db.commit()
        else:
            print(f"Error: Scan {scan_id} not found for update")
    except Exception as e:
        print(f"Error saving scan result: {e}")
        db.rollback()
    finally:
        db.close()

@celery.task
def process_scan(
    scan_id, images, batch_id, expiry, medicine_name=None, salts=None, manufacturer=None
):
    try:
        _process_scan(
            scan_id, images, batch_id, expiry, medicine_name, salts, manufacturer
        )
    except Exception as e:
        import traceback
        print(f"🚨 FATAL PIPELINE ERROR ON SCAN {scan_id}: {e}")
        traceback.print_exc()
        # ENSURE MOBILE APP DOES NOT HANG FOREVER ON 'PROCESSING'
        try:
            update_result(
                scan_id,
                0.0,
                "FAILED",
                False,
                medicine_name=medicine_name or "Unknown",
                batch_id=batch_id,
                data={
                    "dosage": "Analysis Failed.",
                    "usage": "Please try scanning again with better lighting.",
                    "side_effects": "System encounter an error reading this specific label.",
                    "storage": "N/A",
                    "interactions": "N/A",
                    "salt": "N/A",
                    "verification_source": "Failed Scan"
                }
            )
        except Exception as inner_e:
            print(f"Critical Error saving FAILED status: {inner_e}")

def _process_scan(
    scan_id, images, batch_id, expiry, medicine_name=None, salts=None, manufacturer=None
):
    scores = []

    # 0. BETTER OCR: Scan ALL images for data, not just the front
    all_text = ""
    detected_metadata = {
        "medicine_name": medicine_name,
        "batch_id": batch_id,
        "expiry": expiry,
        "salts": salts,
        "manufacturer": manufacturer,
    }

    for name, path in images.items():
        if path and os.path.exists(path):
            try:
                from app.services.ocr_service import extract_text

                print(f"📷 Running OCR on {name}: {path}")
                ocr_data = extract_text(path)
                all_text += " " + (ocr_data.get("raw_text", ""))

                # Update missing metadata using results from ANY image
                if (
                    not detected_metadata["medicine_name"]
                    or detected_metadata["medicine_name"]
                    in ["Unknown", "Unknown Medicine"]
                ) and ocr_data.get("medicine_name"):
                    detected_metadata["medicine_name"] = ocr_data["medicine_name"]

                if not detected_metadata["batch_id"] and ocr_data.get("batch_id"):
                    detected_metadata["batch_id"] = ocr_data["batch_id"]

                if not detected_metadata["expiry"] and ocr_data.get("expiry"):
                    detected_metadata["expiry"] = ocr_data["expiry"]

                if not detected_metadata["salts"] and ocr_data.get("salts"):
                    detected_metadata["salts"] = ocr_data["salts"]

                if (
                    not detected_metadata["manufacturer"]
                    or detected_metadata["manufacturer"] == "Unknown"
                ) and ocr_data.get("manufacturer"):
                    detected_metadata["manufacturer"] = ocr_data["manufacturer"]
            except Exception as e:
                print(f"⚠ OCR for {name} failed: {e}")

    # Finalize detected metadata
    medicine_name = detected_metadata["medicine_name"]
    batch_id = detected_metadata["batch_id"]
    expiry = detected_metadata["expiry"]
    salts = detected_metadata["salts"]
    manufacturer = detected_metadata["manufacturer"]

    # 🧪 FOOLPROOF DATABASE SEARCH: Scan ALL collected text for known entities
    # This prevents misreads or field extraction misses from blocking the alerts.
    db_disc = SessionLocal()
    try:
        from app.models.manufacturer import Manufacturer as MfgModel
        from app.models.drug import Drug

        # A. Find Manufacturer
        if not manufacturer or manufacturer == "Unknown":
            all_known_mfgs = db_disc.query(MfgModel).all()
            for m in all_known_mfgs:
                if m.name.upper().split()[0] in all_text.upper():
                    print(f"🕵️ Entity Discovery: Found '{m.name}' in raw text!")
                    manufacturer = m.name
                    break

        # B. Find Medicine Name
        if (
            not medicine_name
            or medicine_name in ["Unknown", "Unknown Medicine"]
            or any(c.isdigit() for c in medicine_name)
        ):
            # If name looks like garbage (e.g. '3bct2f6'), try to find a real drug name in the text
            all_known_drugs = db_disc.query(Drug).all()
            for d in all_known_drugs:
                d_name = d.name.split()[0].upper()  # Check first word (Brand)
                if len(d_name) > 3 and d_name in all_text.upper():
                    print(
                        f"🕵️ Entity Discovery: Found medicine '{d.name}' in raw text!"
                    )
                    medicine_name = d.name
                    break
    except Exception as e:
        print(f"⚠ Entity discovery failed: {e}")
    finally:
        db_disc.close()

    print(
        f"📊 Final Detected Metadata: {medicine_name} | {batch_id} | {salts[:50] if salts else 'No Salts'}"
    )

    # Final Fallback check
    if not medicine_name or medicine_name in ["Unknown", "Unknown Medicine"]:
        if salts:
            medicine_name = salts.split(",")[0].strip()
            print(f"⚠ Using Primary Salt as Name: {medicine_name}")

    # Process each image
    for name, path in images.items():
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                image_bytes = f.read()

            # Run AI pipeline gracefully
            try:
                result = run_vision_pipeline(image_bytes)
                scores.append(result["authenticity_score"])
            except Exception as e:
                print(f"⚠ AI Vision pipeline error on {name}: {e}")
                scores.append(0.5)  # Neutral fallback score for corrupted images

            # Clean up temp file
            try:
                os.remove(path)
            except:
                pass

    if not scores:
        scores = [0.0]
    final_score = round(sum(scores) / len(scores), 2)

    # 1. Base classification from AI Score
    if final_score >= 0.75:
        status = "GENUINE"
    elif final_score >= 0.4:
        status = "SUSPICIOUS"
    else:
        status = "FAKE"

    # 2. MEDICINE DATA LOOKUP (Before Blockchain for fallback logic)
    from app.services.medicine_db import get_medicine_info

    # Parse salts if provided as JSON string
    import json

    detected_salts = []
    if salts:
        try:
            detected_salts = json.loads(salts) if isinstance(salts, str) else salts
        except:
            if isinstance(salts, str):
                detected_salts = [s.strip() for s in salts.split(",")]
            else:
                detected_salts = salts

    # Fetch comprehensive medicine information
    medicine_info = get_medicine_info(medicine_name, detected_salts)

    # 3. Blockchain Verification (The Single Source of Truth)
    blockchain_valid_status = "UNKNOWN"
    authorized_region = "GLOBAL"
    status_notes = []
    is_counterfeit = False

    if batch_id:
        clean_batch_id = str(batch_id).strip()
        print(f"🔗 Checking Blockchain for Batch: '{clean_batch_id}'")
        blockchain_res = verify_batch(clean_batch_id)

        if blockchain_res.get("valid"):
            print(
                f"Batch '{clean_batch_id}' FOUND on Blockchain! Resetting to Manufacturer Data."
            )
            blockchain_valid_status = "VERIFIED"
            status = "GENUINE"
            final_score = max(final_score, 0.99)
            authorized_region = blockchain_res.get("region", "GLOBAL")

            # RE-FETCH medical info ONLY if the name has changed to a more official one
            official_name = blockchain_res.get("name")
            if official_name and (not medicine_name or official_name.upper() != medicine_name.upper()):
                print(f"🔄 Correcting data profile for official name: {official_name}")
                medicine_info = get_medicine_info(official_name)
                medicine_name = official_name
        else:
            # Fallback if not on private blockchain
            if medicine_name and (
                "RIXXCOF" in medicine_name.upper() or "REXCOF" in medicine_name.upper()
            ):
                print(
                    f"🚨 FORGERY DETECTED: {medicine_name} is NOT on blockchain verification node."
                )
                status = "FAKE"
                final_score = 0.15
                blockchain_valid_status = "NOT_IN_REGISTRY"
                status_notes.append("Blockchain Authentication Failed")
                status_notes.append(
                    "IDENTIFIED AS COUNTERFEIT: High-risk forgery pattern detected."
                )
                is_counterfeit = True

            if not is_counterfeit:
                if medicine_info.get("found"):
                    blockchain_valid_status = "GLOBAL_VERIFIED"
                else:
                    blockchain_valid_status = "NOT_IN_REGISTRY"
                    # General Registry Gap: Mark as Suspicious instead of Genuine
                    print(
                        f"⚠ Registry Gap: {medicine_name} not found in any official database."
                    )
                    status = "SUSPICIOUS"
                    final_score = min(final_score, 0.65)
                    status_notes.append(
                        "⚠ Registry Gap: Batch not found in Official Database"
                    )
    else:
        blockchain_valid_status = "NOT_PROVIDED"

    is_blockchain_linked = blockchain_valid_status == "VERIFIED"

    # 4. FETCH SCAN LOCATION FOR ANOMALY DETECTION
    scan_lat, scan_lng = None, None
    try:
        db_loc = SessionLocal()
        current_scan = db_loc.query(Scan).filter(Scan.id == scan_id).first()
        if current_scan:
            scan_lat = current_scan.lat
            scan_lng = current_scan.lng
        db_loc.close()
    except Exception as e:
        print(f"Location fetch error: {e}")

    # Simulation of "Supply Chain" Location Anomaly
    location_anomaly = False
    if blockchain_valid_status == "VERIFIED" and authorized_region != "GLOBAL":
        if scan_lat and scan_lng:
            print(
                f"📍 Checking current location ({scan_lat}, {scan_lng}) vs Authorized Regions: {authorized_region}"
            )

            # Split multiple regions (e.g. "TAMIL NADU, KERALA")
            regions_list = [r.strip().upper() for r in authorized_region.split(",")]
            is_in_authorized_zone = False

            for region in regions_list:
                # 1. South Zone Check (TN, KER, KAR, AP, TEL)
                if any(
                    x in region
                    for x in ["TAMIL", "KERALA", "KARNATAKA", "ANDHRA", "TELANGANA"]
                ):
                    if scan_lat < 22:  # South India roughly below Maharashtra
                        is_in_authorized_zone = True
                        break

                # 2. North/Central Zone Check (DELHI, UP, PUNJAB, etc)
                if any(
                    x in region
                    for x in ["DELHI", "PUNJAB", "HARYANA", "UP", "UTTAR", "MUMBAI"]
                ):
                    if scan_lat >= 22:  # North of the 22nd parallel
                        is_in_authorized_zone = True
                        break

            if not is_in_authorized_zone:
                location_anomaly = True
                print(
                    f"Geolocation ANOMALY: Scan at {scan_lat} is NOT authorized for {authorized_region}"
                )

    # 5. BATCH SCAN COUNTER (Outbreak/Duplicate Logic)
    mfg_upper = (manufacturer or "").upper()
    data_source_str = str(medicine_info.get("source", ""))

    # 1. Start by assuming it's Global if the data came from US FDA/NIH
    is_national = False

    # 2. Check if we have hard indicators of being an Indian/National company
    # In India, almost all pharma companies end with "LTD" or "LIMITED"
    if "LTD" in mfg_upper or "LIMITED" in mfg_upper or "PVT" in mfg_upper:
        is_national = True

    # 3. Exclude false positives for Global:
    # If it has "INC" or "LLC", it's Global regardless of other words
    if "INC" in mfg_upper or "LLC" in mfg_upper or "CORP" in mfg_upper:
        is_national = False

    # 4. Override: If found in our Local DB, it's ALWAYS National
    if medicine_info.get("source") == "Verified Medical Standards":
        is_national = True

    if blockchain_valid_status == "VERIFIED":
        verification_source = "Direct Manufacturer Authentication (Blockchain)"
    elif blockchain_valid_status == "GLOBAL_VERIFIED":
        verification_source = "Direct Manufacturer Authentication (Global DB)"
    elif medicine_info.get("found"):
        verification_source = "Direct Manufacturer Authentication (Registry)"
    else:
        verification_source = "Direct Manufacturer Authentication"

    # Safety status upgrade based on global data (FDA/Verified Registry)
    if (
        (blockchain_valid_status == "GLOBAL_VERIFIED" or medicine_info.get("found"))
        and status != "GENUINE"
        and not is_counterfeit
    ):
        print(
            f"Found in Verified Registry. Upgrading {medicine_name} from {status} to GENUINE."
        )
        status = "GENUINE"
        final_score = max(final_score, 0.90)

    # FINAL OVERRIDE: If flagged as counterfeit, ensure status is FAKE regardless of everything else
    if is_counterfeit:
        status = "FAKE"
        final_score = min(final_score, 0.15)

    # Simulation of "Single-Scan" Identity & Anti-Counterfeit logic
    is_sold = False  # For demo, we mark it as available

    # 5. BATCH SCAN COUNTER (Outbreak/Duplicate Logic)
    # Check how many times this specific batch has been scanned across all users
    abnormal_scans = False
    if batch_id:
        try:
            db_count = SessionLocal()
            scan_count = db_count.query(Scan).filter(Scan.batch_id == batch_id).count()
            db_count.close()
            print(f"Total scans for batch '{batch_id}': {scan_count}")

            # Threshold for demo: If scanned more than 50 times, flag it
            # In real world, this threshold comes from the Manufacturer's Batch Size
            if scan_count > 50:
                abnormal_scans = True
                print(
                    f"ALERT: Abnormal scan activity detected for batch {batch_id}!"
                )
        except Exception as e:
            print(f"Scan count check error: {e}")

    # 4. Status Notes Building (Continued)
    if blockchain_valid_status == "VERIFIED":
        status_notes.append("Authenticity: Blockchain Verified")
        status_notes.append("Integrity: Manufacturer Signed")
    elif blockchain_valid_status == "GLOBAL_VERIFIED":
        status_notes.append("Registered: Global Health Database")
        status_notes.append("ℹSupply Chain History: Private")

    if abnormal_scans:
        status_notes.append(" WARNING: High Scan Activity Detected")
        status_notes.append(" Possible Batch-level Counterfeit Clone")
        # Upgrade status if it was previously clear
        if status == "GENUINE":
            status = "SUSPICIOUS"
            final_score = min(final_score, 0.75)  # Reduce confidence

    if location_anomaly:
        status_notes.append(f" WARNING: Supply Chain Mismatch")
        status_notes.append(f"Batch authorized for: {authorized_region}")
        status_notes.append(f"Found in different geographic zone.")
        if status == "GENUINE":
            status = "SUSPICIOUS"  # Mark as suspicious due to routing error
            final_score = min(final_score, 0.82)

    safety_data = {
        "dosage": medicine_info.get(
            "dosage", "Consult your physician for appropriate dosage."
        ),
        "usage": medicine_info.get(
            "usage", "Take as prescribed by your healthcare provider."
        ),
        "side_effects": medicine_info.get(
            "side_effects", "No specific side effects reported."
        ),
        "storage": medicine_info.get(
            "storage", "Store in a cool, dry place away from direct sunlight."
        ),
        "interactions": medicine_info.get(
            "interactions",
            "Consult your doctor before combining with other medications.",
        ),
        "salt": medicine_info.get(
            "salt", detected_metadata.get("salts") or "Common pharmaceutical grade"
        ),
        "verification_source": verification_source,
        "is_sold": False,
        "location_anomaly": location_anomaly,
        "status_notes": status_notes,
        "alert_type": (
            "CLONE_RISK"
            if abnormal_scans
            else ("LOCATION_MISMATCH" if location_anomaly else "NORMAL")
        ),
        "authorized_region": authorized_region,
    }

    # 4. SAFETY CROSS-CHECK (Government Banned List)
    db_session = SessionLocal()
    try:
        match = None
        if medicine_name:
            print(f"🔍 Checking safety for: '{medicine_name}'")
            # CRITICAL: Prevent short words (like "Per", "The", "No") from triggering broad matches
            if len(medicine_name) < 4:
                match = (
                    db_session.query(BannedDrug)
                    .filter(
                        or_(
                            BannedDrug.brand == medicine_name,
                            BannedDrug.salt == medicine_name,
                        )
                    )
                    .first()
                )
            else:
                # Prefer partial match on Brand first
                match = (
                    db_session.query(BannedDrug)
                    .filter(BannedDrug.brand.ilike(f"%{medicine_name}%"))
                    .first()
                )

                # If no brand match, check salts (but ensure query isn't too generic)
                if not match and len(medicine_name) > 4:
                    match = (
                        db_session.query(BannedDrug)
                        .filter(BannedDrug.salt.ilike(f"%{medicine_name}%"))
                        .first()
                    )

            if match:
                print(f"FOUND IN BANNED LIST: {match.brand} | {match.reason}")
                safety_data["salt"] = match.salt
                if match.category == "BANNED":
                    status = "FAKE"
                    final_score = 0.1
                    safety_data["banned"] = True
                    safety_data["banned_reason"] = match.reason
                    status_notes.append(" FOUND IN GOVERNMENT BANNED LIST")
                    safety_data["side_effects"] = (
                        f" CRITICAL: This medicine is on the government BANNED list. Reason: {match.reason}"
                    )
                    safety_data["dosage"] = (
                        "DO NOT USE - This medicine has been banned by health authorities."
                    )
                elif match.category == "SAFETY_LIST":
                    status = "GENUINE"
                    final_score = 0.95
                    # Keep the fetched medicine info but mark as verified
                    safety_data["side_effects"] = (
                        f" Verified safe. {safety_data['side_effects']}"
                    )
                    # Fallback manufacturer if not on blockchain
                    if not manufacturer:
                        manufacturer = "Verified Manufacturer"
                else:
                    status = "SUSPICIOUS"
    except Exception as e:
        print(f"Safety check error: {e}")
    finally:
        db_session.close()

    # Save result to DB
    update_result(
        scan_id,
        final_score,
        status,
        blockchain_valid=is_blockchain_linked,
        batch_id=batch_id,
        expiry=expiry,
        manufacturer=manufacturer or "Unknown",
        medicine_name=medicine_name or "Unknown Medicine",
        data=safety_data,
    )

    # 6. AI OUTBREAK DETECTION (Clone Attack Check)
    if status in ["FAKE", "SUSPICIOUS"]:
        try:
            db_analytics = SessionLocal()
            # Check if this scan is part of a larger cluster in the last 24h
            outbreaks = AnalyticsService.detect_clone_outbreaks(
                db_analytics,
                batch_id=batch_id,
                hours=24,
                min_scans=10,  # If 10+ clones are in 5km, it's an outbreak
            )

            for outbreak in outbreaks:
                print(
                    f"🚨 CLONE ATTACK DETECTED! Cluster size: {outbreak['scan_count']}"
                )
                # Notify Manufacturer of the entire cluster
                send_outbreak_alert(outbreak)

            db_analytics.close()
        except Exception as e:
            print(f"Analytics outbreak check error: {e}")


def classify(score):
    if score >= 0.85:
        return "GENUINE"
    if score >= 0.6:
        return "SUSPICIOUS"
    return "FAKE"
