from sqlalchemy import Column, String, Integer, DateTime, Boolean, text
from sqlalchemy.sql import func
from app.db.session import Base

class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, index=True, nullable=False)
    security_email = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)

    blockchain_address = Column(String, nullable=True)

    status = Column(String, server_default="UNVERIFIED", nullable=False)
    verification_code = Column(String, nullable=True)

    email_verified = Column(Boolean, server_default=text("false"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())