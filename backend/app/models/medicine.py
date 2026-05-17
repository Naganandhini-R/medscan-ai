from sqlalchemy import Column, String, Integer, Text
from app.db.session import Base

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    salt = Column(Text, nullable=True)
    dosage = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    storage = Column(Text, nullable=True)
    manufacturer = Column(String, nullable=True)
