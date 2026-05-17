from sqlalchemy import Column, String, Integer, Text
from app.db.session import Base

class BannedDrug(Base):
    __tablename__ = "banned_drugs"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True, nullable=True)
    salt = Column(
        Text, index=True, nullable=True
    )  # Text because salts can be long FDCs
    category = Column(String, nullable=True)  # Prohibited, Restricted, Banned
    source = Column(String, nullable=True)  # PDF filename or year
    reason = Column(Text, nullable=True)
