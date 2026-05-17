from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.logging import logger

router = APIRouter()


@router.get("/")
async def health_check():
    """
    Health check endpoint to verify backend and database connectivity.
    """
    db = SessionLocal()
    try:
        # Check Database
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
    finally:
        db.close()
