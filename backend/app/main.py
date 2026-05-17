from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.v1.scan import router as scan_router
from app.api.v1.health import router as health_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.report import router as report_router
from app.api.v1.auth import router as auth_router
from app.api.v1.medicine import router as medicine_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.manufacturer import router as manufacturer_router
from app.admin.routes import router as admin_router

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Try-except block for blockchain import to prevent app crash if dependencies fail
try:
    from app.blockchain.web3_client import get_contract

    blockchain_active = get_contract() is not None
except ImportError as e:
    print(f"⚠ Blockchain dependency missing or error: {e}")
    blockchain_active = False

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="MedScan-AI Backend",
    version="1.0.0",
    description="Backend API for MedScan-AI",
)
app.state.limiter = limiter


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f" Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# -----------------------------
# CORS Middleware
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Include routers
# -----------------------------
from app.api.v1.scan import router as scan_router
from app.api.v1.health import router as health_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.report import router as report_router
from app.api.v1.auth import router as auth_router
from app.api.v1.medicine import router as medicine_router
from app.api.v1.manufacturer import router as manufacturer_router
from app.api.v1.analytics import router as analytics_router

app.include_router(scan_router, prefix="/api/v1/scan", tags=["Scan"])
app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
app.include_router(chatbot_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(report_router, prefix="/api/v1/report", tags=["Report"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(
    medicine_router, prefix="/api/v1/medicine", tags=["Medicine Registry"]
)
app.include_router(
    manufacturer_router, prefix="/api/v1/manufacturer", tags=["Manufacturer Profile"]
)
app.include_router(
    analytics_router, prefix="/api/v1/analytics", tags=["Forensic Analytics"]
)
app.include_router(admin_router, prefix="/api/v1", tags=["Admin"])


# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
async def root():
    return {"message": "Welcome to MedScan-AI API", "status": "running"}


# -----------------------------
# Startup event
# -----------------------------
from app.db.session import engine, Base

# Import models to ensure they are registered
from app.models.scan import Scan
from app.models.user import User
from app.models.medicine import Medicine
from app.models.report import IssueReport
from app.models.manufacturer import Manufacturer


@app.on_event("startup")
async def startup_event():
    try:
        from sqlalchemy import text

        with engine.connect() as conn:
            # Check for manufacturers table columns
            res = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='manufacturers' AND column_name='status';"
                )
            ).fetchone()
            if not res:
                print("DEBUG: Adding status column to manufacturers...")
                conn.execute(
                    text(
                        "ALTER TABLE manufacturers ADD COLUMN status VARCHAR DEFAULT 'UNVERIFIED' NOT NULL;"
                    )
                )

            res = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='manufacturers' AND column_name='verification_code';"
                )
            ).fetchone()
            if not res:
                print("DEBUG: Adding verification_code column...")
                conn.execute(
                    text(
                        "ALTER TABLE manufacturers ADD COLUMN verification_code VARCHAR;"
                    )
                )

            res = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns WHERE table_name='manufacturers' AND column_name='email_verified';"
                )
            ).fetchone()
            if not res:
                print("DEBUG: Adding email_verified column...")
                conn.execute(
                    text(
                        "ALTER TABLE manufacturers ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;"
                    )
                )

            # Check for scans table columns
            columns = [
                ("lat", "FLOAT"),
                ("lng", "FLOAT"),
                ("user_id", "VARCHAR"),
                ("data", "JSON"),
                ("expiry", "VARCHAR"),
                ("manufacturer", "VARCHAR"),
                ("medicine_name", "VARCHAR"),
                ("batch_id", "VARCHAR"),
                ("blockchain_valid", "BOOLEAN"),
            ]
            res_tables = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_name='scans';"
                )
            ).fetchone()
            if res_tables:
                for col, col_type in columns:
                    query = text(
                        f"SELECT column_name FROM information_schema.columns WHERE table_name='scans' AND column_name='{col}';"
                    )
                    res = conn.execute(query).fetchone()
                    if not res:
                        print(f"DEBUG: Adding {col} to scans...")
                        conn.execute(
                            text(f"ALTER TABLE scans ADD COLUMN {col} {col_type};")
                        )

            # Check for issue_reports table columns
            res_reports = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_name='issue_reports';"
                )
            ).fetchone()
            if res_reports:
                res = conn.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name='issue_reports' AND column_name='manufacturer';"
                    )
                ).fetchone()
                if not res:
                    print("DEBUG: Adding manufacturer column to issue_reports...")
                    conn.execute(
                        text(
                            "ALTER TABLE issue_reports ADD COLUMN manufacturer VARCHAR;"
                        )
                    )

            conn.commit()
        Base.metadata.create_all(bind=engine)
        print("Database tables ready")
    except Exception as e:
        print(f" Database setup error: {e}")

    if not blockchain_active:
        print("⚠ Blockchain disabled")


# -----------------------------
# Shutdown event
# -----------------------------
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down MedScan-AI backend...")
