from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class Scan(Base):
    __tablename__ = "scans"

    # Primary key
    id = Column(String, index=True, primary_key=True, default=lambda: str(uuid.uuid4()))

    # AI result
    score = Column(Float, nullable=True)
    status = Column(String, default="PROCESSING")

    # Blockchain verification
    blockchain_valid = Column(Boolean, default=False)

    # Metadata
    medicine_name = Column(String, index=True, nullable=True)
    batch_id = Column(String, nullable=True)
    expiry = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)

    # Extra safety/classification data
    data = Column(JSON, nullable=True)

    # Optional geolocation (for admin heatmap)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)

    # User context
    user_id = Column(String, index=True, nullable=True)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
