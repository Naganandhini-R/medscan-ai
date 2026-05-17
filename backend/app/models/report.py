from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class IssueReport(Base):
    __tablename__ = "issue_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id"), nullable=True)
    medicine_name = Column(String, index=True)
    batch_id = Column(String, index=True)
    manufacturer = Column(String, index=True, nullable=True)
    issue_type = Column(String)  # e.g., 'Counterfeit Suspected'
    location_details = Column(String)  # User entered shop name/address
    description = Column(Text)

    # Coordinates at the time of reporting
    lat = Column(String, nullable=True)
    lng = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
