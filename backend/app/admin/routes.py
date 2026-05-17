from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.scan import Scan

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def dashboard_stats(user_id: str = None, db: Session = Depends(get_db)):
    def get_count(status=None):
        q = db.query(Scan)
        if user_id:
            q = q.filter(Scan.user_id == user_id)
        if status:
            q = q.filter(Scan.status == status)
        return q.count()

    return {
        "total_scans": get_count(),
        "fake_detected": get_count("FAKE"),
        "suspicious": get_count("SUSPICIOUS"),
        "genuine": get_count("GENUINE"),
    }


@router.get("/heatmap")
def heatmap(db: Session = Depends(get_db)):
    scans = db.query(Scan).filter(Scan.status == "FAKE").all()
    return [{"lat": s.lat, "lng": s.lng, "score": s.score} for s in scans]


@router.get("/nearby-fakes")
def nearby_fakes(
    lat: float, lng: float, radius_km: float = 5, db: Session = Depends(get_db)
):
    scans = db.query(Scan).filter(Scan.status == "FAKE").all()

    def distance(s_obj, target):
        from math import radians, cos, sin, sqrt, atan2

        if s_obj.lat is None or s_obj.lng is None:
            return float("inf")

        R = 6371.0  # Earth radius in km
        lat1, lon1 = radians(s_obj.lat), radians(s_obj.lng)
        lat2, lon2 = radians(target[0]), radians(target[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        a = min(1.0, max(0.0, a))  # prevent floating point math domain errors

        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    return [
        {"lat": s.lat, "lng": s.lng, "score": s.score}
        for s in scans
        if distance(s, (lat, lng)) <= radius_km
    ]


@router.get("/recent")
def recent_scans(limit: int = 20, user_id: str = None, db: Session = Depends(get_db)):
    query = db.query(Scan)
    if user_id:
        query = query.filter(Scan.user_id == user_id)
    scans = query.order_by(Scan.created_at.desc()).limit(limit).all()
    return scans


from app.models.report import IssueReport

@router.get("/reports")
def get_security_reports(limit: int = 50, db: Session = Depends(get_db)):
    reports = (
        db.query(IssueReport).order_by(IssueReport.created_at.desc()).limit(limit).all()
    )
    return reports
