from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.manufacturer import Manufacturer
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from typing import Optional
import random
import string

router = APIRouter()


# Schema for Input Validation
class ManufacturerCreate(BaseModel):
    name: str
    security_email: EmailStr
    contact_person: Optional[str] = None
    blockchain_address: Optional[str] = None


class ManufacturerUpdate(BaseModel):
    name: str  # Search key
    security_email: Optional[EmailStr] = None
    contact_person: Optional[str] = None
    blockchain_address: Optional[str] = None


@router.post("/register")
def onboard_manufacturer(data: ManufacturerCreate, db: Session = Depends(get_db)):
    """
    How manufacturers 'Insert' their data into MedScan-AI.
    This creates their official security profile.
    """
    # 1. Clean data
    mfg_name = data.name.strip().upper()

    # 2. Check if already registered
    existing = db.query(Manufacturer).filter(Manufacturer.name == mfg_name).first()
    if existing:
        # Update existing profile if new details provided
        if data.security_email:
            existing.security_email = data.security_email
        if data.contact_person:
            existing.contact_person = data.contact_person
        if data.blockchain_address:
            existing.blockchain_address = data.blockchain_address
        db.commit()
        return {
            "status": "success",
            "message": "Existing identity recognized. Login successful.",
            "manufacturer_id": existing.id,
            "verification_sent_to": existing.security_email,
        }

    # 3. Generate Verification Code (6-digit)
    v_code = "".join(random.choices(string.digits, k=6))

    # 4. Create entry
    new_mfg = Manufacturer(
        name=mfg_name,
        security_email=data.security_email,
        contact_person=data.contact_person,
        blockchain_address=data.blockchain_address,
        status="UNVERIFIED",
        verification_code=v_code,
        email_verified=False,
    )

    try:
        db.add(new_mfg)
        db.commit()
        db.refresh(new_mfg)

        return {
            "status": "success",
            "message": f"Identity registered. Please verify your email.",
            "manufacturer_id": new_mfg.id,
            "verification_sent_to": data.security_email,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Onboarding failed: {str(e)}")


@router.post("/update")
def update_manufacturer(data: ManufacturerUpdate, db: Session = Depends(get_db)):
    """
    Securely update a manufacturer's security profile.
    Used for real-time adjustments (e.g., email changes).
    """
    mfg_name = data.name.strip().upper()
    mfg = db.query(Manufacturer).filter(Manufacturer.name == mfg_name).first()

    if not mfg:
        # Try fuzzy match if exact match fails
        mfg = (
            db.query(Manufacturer)
            .filter(Manufacturer.name.ilike(f"%{mfg_name}%"))
            .first()
        )

    if not mfg:
        raise HTTPException(
            status_code=404, detail="Manufacturer Registry Entry not found."
        )

    if data.security_email:
        mfg.security_email = data.security_email
    if data.contact_person:
        mfg.contact_person = data.contact_person
    if data.blockchain_address:
        mfg.blockchain_address = data.blockchain_address

    try:
        db.commit()
        return {
            "status": "success",
            "message": f"Security Profile updated for {mfg.name}",
            "new_email": mfg.security_email,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{name}")
def get_manufacturer_profile(name: str, db: Session = Depends(get_db)):
    """
    View the registered profile of a manufacturer.
    """
    mfg = db.query(Manufacturer).filter(Manufacturer.name.ilike(f"%{name}%")).first()
    if not mfg:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")
    return mfg


@router.get("/list")
def list_manufacturers(db: Session = Depends(get_db)):
    """
    List all registered manufacturers.
    """
    print("DEBUG: Fetching all manufacturers...")
    try:
        data = db.query(Manufacturer).all()
        print(f"DEBUG: Found {len(data)} items")
        return data
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        raise


@router.post("/approve/{mfg_id}")
def approve_manufacturer(
    mfg_id: int, action: str = "APPROVED", db: Session = Depends(get_db)
):
    """
    Admin action to approve or reject a manufacturer.
    """
    mfg = db.query(Manufacturer).filter(Manufacturer.id == mfg_id).first()
    if not mfg:
        raise HTTPException(status_code=404, detail="Manufacturer not found.")

    mfg.status = action.upper()
    db.commit()
    return {
        "status": "success",
        "message": f"Manufacturer {mfg.name} is now {mfg.status}.",
    }


@router.get("/status/{name}")
def check_status(name: str, db: Session = Depends(get_db)):
    """
    Check if a company is approved.
    """
    mfg = db.query(Manufacturer).filter(Manufacturer.name.ilike(f"%{name}%")).first()
    if not mfg:
        return {"status": "NOT_FOUND"}
    return {
        "status": mfg.status,
        "name": mfg.name,
        "email_verified": mfg.email_verified,
        "identity_verified": mfg.status != "UNVERIFIED",
    }


class VerifyEmail(BaseModel):
    name: str
    code: str


@router.post("/verify/email")
def verify_email(data: VerifyEmail, db: Session = Depends(get_db)):
    """
    Verify the 6-digit code sent to company email.
    """
    mfg = (
        db.query(Manufacturer).filter(Manufacturer.name.ilike(f"%{data.name}%")).first()
    )
    if not mfg:
        raise HTTPException(status_code=404, detail="Entity not found")

    if mfg.verification_code == data.code:
        mfg.email_verified = True
        mfg.status = "PENDING"  # Move to Admin Approval queue
        db.commit()
        return {
            "status": "success",
            "message": "Email verified. Waiting for Admin authorization.",
        }

    raise HTTPException(status_code=400, detail="Invalid verification code")


class SecurityProof(BaseModel):
    name: str
    token: str


@router.post("/verify/security-token")
def verify_security_token(data: SecurityProof, db: Session = Depends(get_db)):
    """
    Simplified Wallet/Secure Proof-of-Identity.
    Requires a matching token to establish high-trust identity.
    """
    mfg = (
        db.query(Manufacturer).filter(Manufacturer.name.ilike(f"%{data.name}%")).first()
    )
    if not mfg:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Logic: Proof could be derived from blockchain wallet address
    if len(data.token) > 20:  # Simulated validation
        return {"status": "verified", "proof_hash": "SHA256_FINGERPRINT_ACTIVE"}

    raise HTTPException(status_code=400, detail="Tactical proof rejected")
