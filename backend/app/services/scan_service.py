import uuid
import os
import aiofiles
from app.tasks.worker import process_scan
from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.scan import Scan

UPLOAD_DIR = "temp/medscan"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def save_file(file, scan_id, name):
    try:
        path = f"{UPLOAD_DIR}/{scan_id}_{name}.jpg"
        async with aiofiles.open(path, "wb") as out_file:
            content = await file.read()  # Async read
            await out_file.write(content)  # Async write
        return path
    except Exception as e:
        logger.error(f"Failed to save file {name} for scan {scan_id}: {e}")
        raise e


async def enqueue_scan(
    front,
    back,
    strip,
    medicine_name,
    batch_id,
    expiry,
    salts=None,
    manufacturer=None,
    user_id=None,
):
    logger.info("enqueue_scan REACHED")
    scan_id = str(uuid.uuid4())
    logger.info(f"Enqueuing scan {scan_id} for user {user_id}")

    # Process files asynchronously
    front_path = await save_file(front, scan_id, "front")
    back_path = await save_file(back, scan_id, "back") if back else None
    strip_path = await save_file(strip, scan_id, "strip") if strip else None

    # Create Initial DB Entry as PROCESSING
    db = SessionLocal()
    try:
        new_scan = Scan(
            id=scan_id,
            status="PROCESSING",
            score=0.0,
            blockchain_valid=False,
            medicine_name=medicine_name,
            user_id=user_id,
        )
        db.add(new_scan)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to create initial DB record: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

    images = {"front": front_path, "back": back_path, "strip": strip_path}

    # Offload heavy processing to Celery
    process_scan.delay(
        scan_id, images, batch_id, expiry, medicine_name, salts, manufacturer
    )

    return scan_id
