from app.db.session import SessionLocal
from app.models.scan import Scan
from app.models.medicine import Medicine
from app.models.manufacturer import Manufacturer
from app.models.report import IssueReport


def reset_database():
    db = SessionLocal()
    print("🧹 Cleaning MedScan-AI Data Ecosystem...")
    try:
        # Delete all telemetry and registry data
        db.query(Scan).delete()
        db.query(IssueReport).delete()
        db.query(Medicine).delete()
        db.query(Manufacturer).delete()

        db.commit()
        print(" Database cleared successfully! The system is now in a PURE 0 state.")
    except Exception as e:
        db.rollback()
        print(f" Error during cleanup: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
