from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from app.services.scan_service import enqueue_scan
from app.db.session import get_db
from app.models.scan import Scan
from app.core.logging import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
from typing import Optional, Any
import time

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Response Models
class ScanResponse(BaseModel):
    scan_id: str
    status: str


class ScanResultResponse(BaseModel):
    id: str
    score: float
    status: str
    blockchain_valid: bool
    medicine_name: Optional[str] = None
    batch_id: Optional[str] = None
    expiry: Optional[str] = None
    manufacturer: Optional[str] = None
    data: Optional[Any] = None
    created_at: Any


MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/jpg"]


async def validate_file(file: UploadFile):
    if file.filename == "":
        return None

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only JPEG/PNG allowed.",
        )

    # Check file size (approximate by seeking)
    # Note: efficient size check depends on backend middleware, but this is a basic check
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Limit is 50MB.")
    return file


@router.post("/verify", response_model=ScanResponse)
@limiter.limit("5/minute")
async def verify_medicine(
    request: Request,
    front: UploadFile = File(...),
    back: UploadFile = File(None),
    strip: UploadFile = File(None),
    medicine_name: str = Form(None),
    batch_id: str = Form(None),
    expiry: str = Form(None),
    salts: str = Form(None),
    manufacturer: str = Form(None),
    user_id: str = Form(None),
):  
    logger.info("VERIFY API CALLED") 
    # Validate Inputs
    await validate_file(front)
    if back:
        await validate_file(back)
    if strip:
        await validate_file(strip)

    try:
        scan_id = await enqueue_scan(
            front,
            back,
            strip,
            medicine_name,
            batch_id,
            expiry,
            salts,
            manufacturer,
            user_id,
        )
        return {"scan_id": scan_id, "status": "PROCESSING"}
    except Exception as e:
        logger.error(f"Scan enqueue failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process scan")


@router.get("/result/{scan_id}", response_model=ScanResultResponse)
def get_result(scan_id: str, db=Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan
