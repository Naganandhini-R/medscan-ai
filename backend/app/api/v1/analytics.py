from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.analytics_service import AnalyticsService
from typing import List, Optional

router = APIRouter()


@router.get("/outbreaks")
def get_outbreaks(
    batch_id: Optional[str] = None,
    manufacturer: Optional[str] = None,
    medicine: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """
    Get detected AI 'Clone Attack' outbreaks.
    """
    try:
        outbreaks = AnalyticsService.detect_clone_outbreaks(
            db,
            batch_id=batch_id,
            manufacturer=manufacturer,
            medicine_name=medicine,
            hours=hours,
        )
        return {"status": "success", "count": len(outbreaks), "data": outbreaks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed-outbreaks")
def seed_outbreaks(db: Session = Depends(get_db)):
    """
    Pure Logic Seeding.
    Zero hardcoded strings. Seeds telemetry only for medicines already in life-cycle.
    """
    import random
    from datetime import datetime
    from app.models.scan import Scan
    from app.models.manufacturer import Manufacturer
    from app.models.medicine import Medicine
    from app.models.report import IssueReport

    # Fetch real assets from DB
    existing_medicines = db.query(Medicine).all()

    if not existing_medicines:
        raise HTTPException(
            status_code=400,
            detail="Forensic Registry Empty: Please register a company and batch via Protocol first.",
        )

    # Expanded geographic distribution nodes
    locations = [
        {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
        {"name": "Delhi", "lat": 28.6139, "lng": 77.2090},
        {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
        {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946},
        {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
        {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
        {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
        {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
        {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873},
        {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462},
    ]

    report_descriptions = [
        "Seal was already broken when I bought it.",
        "The QR code on the back doesn't scan properly.",
        "Color of the tablet looks different than usual.",
        "Price was suspiciously low at the local pharmacy.",
        "Found this batch being sold without prescription in a small shop.",
        "Printing on the box is blurry and easy to rub off.",
        "Chemical smell is very strong, unlike previous strips.",
        "Expiry date seems to be over-printed manually.",
    ]

    # Seed unique telemetry for EACH registered asset with HIGH VARIANCE
    for med in existing_medicines:
        # Each brand has a unique footprint
        brand_multiplier = random.uniform(0.5, 2.0)

        # A. Genuine Scans (High variance per brand)
        gen_count = int(random.randint(10, 60) * brand_multiplier)
        for _ in range(gen_count):
            loc = random.choice(locations)
            scan = Scan(
                medicine_name=med.name,
                batch_id=f"B-{random.randint(100,999)}",
                manufacturer=med.manufacturer,
                status="GENUINE",
                lat=loc["lat"] + random.uniform(-0.15, 0.15),
                lng=loc["lng"] + random.uniform(-0.15, 0.15),
                created_at=datetime.utcnow(),
            )
            db.add(scan)

        # B. Suspicious Scans
        susp_count = random.randint(2, 12)
        for _ in range(susp_count):
            loc = random.choice(locations)
            scan = Scan(
                medicine_name=med.name,
                batch_id=f"S-{random.randint(10,99)}",
                manufacturer=med.manufacturer,
                status="SUSPICIOUS",
                lat=loc["lat"] + random.uniform(-0.3, 0.3),
                lng=loc["lng"] + random.uniform(-0.3, 0.3),
                created_at=datetime.utcnow(),
            )
            db.add(scan)

        # C. Targeted Attacks (Some brands heavily attacked, some not at all)
        threat_profile = random.random()
        if threat_profile > 0.3:  # 70% chance of threat presence
            fake_count = int(
                random.randint(10, 40) * (1.2 if threat_profile > 0.8 else 1.0)
            )
            # Pick a specific "outbreak" city for duplicates
            center = random.choice(locations)
            for _ in range(fake_count):
                scan = Scan(
                    medicine_name=med.name,
                    batch_id=f"X-{random.randint(10,99)}",
                    manufacturer=med.manufacturer,
                    status="FAKE",
                    lat=center["lat"] + random.uniform(-0.08, 0.08),
                    lng=center["lng"] + random.uniform(-0.08, 0.08),
                    created_at=datetime.utcnow(),
                )
                db.add(scan)

            # D. Seed Forensic User Reports for attacks
            report_count = random.randint(2, 5)
            for _ in range(report_count):
                loc = random.choice(locations)
                report = IssueReport(
                    medicine_name=med.name,
                    batch_id=f"X-{random.randint(10,99)}",
                    manufacturer=med.manufacturer,
                    issue_type="Counterfeit Suspected",
                    location_details=f"{loc['name']} Pharmacy Node",
                    description=random.choice(report_descriptions),
                    lat=str(loc["lat"] + random.uniform(-0.1, 0.1)),
                    lng=str(loc["lng"] + random.uniform(-0.1, 0.1)),
                    created_at=datetime.utcnow(),
                )
                db.add(report)

    db.commit()
    return {
        "status": "success",
        "message": f"Global Forensic Network (Scans & Reports) updated for {len(existing_medicines)} assets.",
    }


@router.post("/clear-telemetry")
def clear_telemetry(db: Session = Depends(get_db)):
    """
    Forensic Purge: Removes all scan telemetry to reset the network to a pure 0 state.
    """
    from app.models.scan import Scan

    try:
        db.query(Scan).delete()
        db.commit()
        return {
            "status": "success",
            "message": "Global telemetry purged. Network reset to 0.",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
def get_heatmap(
    manufacturer: Optional[str] = None,
    medicine: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get raw data points for the manufacturer heatmap.
    """
    try:
        points = AnalyticsService.get_heatmap_data(
            db, manufacturer=manufacturer, medicine_name=medicine
        )
        return {"status": "success", "count": len(points), "data": points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline")
def get_timeline(
    manufacturer: Optional[str] = None,
    medicine: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get scan frequency over time (Last 24 hours).
    """
    from datetime import datetime, timedelta
    from app.models.scan import Scan
    from sqlalchemy import func

    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    query = db.query(
        func.extract("hour", Scan.created_at).label("hour"),
        func.count(Scan.id).label("count"),
    ).filter(Scan.created_at >= day_ago)

    if manufacturer:
        query = query.filter(Scan.manufacturer.ilike(f"%{manufacturer}%"))

    if medicine:
        query = query.filter(Scan.medicine_name.ilike(f"%{medicine}%"))

    results = query.group_by("hour").all()

    # Fill gaps for 24 hours (12 slots of 2 hours for simpler chart)
    timeline = [0] * 12
    for r in results:
        slot = int(r.hour) // 2
        if slot < 12:
            timeline[slot] += r.count

    return {"status": "success", "data": timeline}
