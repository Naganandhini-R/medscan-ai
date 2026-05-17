import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.scan import Scan
from app.core.security import get_password_hash

def restore_user_and_scans():
    db = SessionLocal()
    
    email = "naganandhini2712@gmail.com"
    full_name = "Naganandhini"
    hashed = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQG8.hqK" # hash for "password"
    
    # 1. Create or update the user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed,
            is_active=True,
            has_boarded=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {email}")
    else:
        user.hashed_password = hashed
        db.commit()
        print(f"Updated password for existing user: {email}")

    # 2. Assign all existing scans to this user
    scans = db.query(Scan).all()
    count = 0
    for scan in scans:
        scan.user_id = str(user.id)
        count += 1
        
    db.commit()
    print(f"Assigned {count} scans to user {email}")
    
    db.close()

if __name__ == "__main__":
    restore_user_and_scans()
