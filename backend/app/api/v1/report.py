from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.scan import Scan
from app.models.report import IssueReport
from app.models.manufacturer import Manufacturer
from app.services.email_service import send_security_alert
from app.services.report_service import ForensicReportService
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter()


class ReportSubmit(BaseModel):
    scan_id: Optional[str] = None
    medicine_name: str
    batch_id: str
    issue_type: str
    location_details: str
    description: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    manufacturer: Optional[str] = None


@router.post("/submit")
async def submit_report(
    data: ReportSubmit, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    try:
        new_report = IssueReport(
            scan_id=data.scan_id,
            medicine_name=data.medicine_name,
            batch_id=data.batch_id,
            manufacturer=data.manufacturer,
            issue_type=data.issue_type,
            location_details=data.location_details,
            description=data.description,
            lat=str(data.lat) if data.lat else None,
            lng=str(data.lng) if data.lng else None,
        )

        # 🛡️ DYNAMIC FORENSIC SYNC: If scan_id exists, fetch manufacturer from it if not provided
        if data.scan_id:
            scan = db.query(Scan).filter(Scan.id == data.scan_id).first()
            if scan:
                if not new_report.manufacturer:
                    new_report.manufacturer = scan.manufacturer

                # Update scan status if report is about Counterfeit
                if data.issue_type == "Counterfeit Suspected":
                    scan.status = "FAKE"

        db.add(new_report)
        db.commit()

        # 🚀 TRIGGER AUTOMATED EMAIL ALERT (Background)
        background_tasks.add_task(send_security_alert, data)

        return {"success": True, "message": "Report saved and alert sent successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate-forensic/{scan_id}")
async def generate_forensic_report(scan_id: str, db: Session = Depends(get_db)):
    """
    Triggers the generation of a professional forensic PDF report for a scan.
    """
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found")

    # Fetch manufacturer info for blockchain wallet details
    mfg = db.query(Manufacturer).filter(Manufacturer.name == scan.manufacturer).first()

    try:
        service = ForensicReportService(db)
        filepath, filename = service.generate_scan_report(scan, mfg)

        if os.path.exists(filepath):
            return FileResponse(
                path=filepath, filename=filename, media_type="application/pdf"
            )
        else:
            raise HTTPException(status_code=500, detail="Report generation failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_report_stats(
    manufacturer: Optional[str] = None,
    medicine: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Scan)
    report_query = db.query(IssueReport)

    if manufacturer:
        m_pattern = f"%{manufacturer}%"
        query = query.filter(Scan.manufacturer.ilike(m_pattern))
        # IMPROVED: Check both direct manufacturer on report AND fallback medicine/scan mapping
        report_query = report_query.filter(
            (IssueReport.manufacturer.ilike(m_pattern))
            | (
                IssueReport.medicine_name.in_(
                    db.query(Scan.medicine_name)
                    .filter(Scan.manufacturer.ilike(m_pattern))
                    .subquery()
                )
            )
        )

    if medicine:
        query = query.filter(Scan.medicine_name.ilike(f"%{medicine}%"))
        report_query = report_query.filter(
            IssueReport.medicine_name.ilike(f"%{medicine}%")
        )

    total_scans = query.count()
    fake_count = query.filter(Scan.status == "FAKE").count()
    real_count = query.filter(Scan.status == "GENUINE").count()
    suspicious_count = query.filter(Scan.status == "SUSPICIOUS").count()

    total_reports = report_query.count()

    return {
        "total_scans": total_scans,
        "total_reports": total_reports,
        "scans_by_status": {
            "fake": fake_count,
            "genuine": real_count,
            "suspicious": suspicious_count,
        },
    }


@router.get("/list")
async def list_reports(
    manufacturer: Optional[str] = None,
    medicine: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(IssueReport)
    if manufacturer:
        m_pattern = f"%{manufacturer}%"
        query = query.filter(
            (IssueReport.manufacturer.ilike(m_pattern))
            | (
                IssueReport.medicine_name.in_(
                    db.query(Scan.medicine_name)
                    .filter(Scan.manufacturer.ilike(m_pattern))
                    .subquery()
                )
            )
        )
    if medicine:
        query = query.filter(IssueReport.medicine_name.ilike(f"%{medicine}%"))

    reports = query.order_by(IssueReport.created_at.desc()).limit(50).all()
    return reports
