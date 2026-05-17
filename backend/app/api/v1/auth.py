from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from pydantic import BaseModel, EmailStr

router = APIRouter()


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


from app.core.security import get_password_hash, verify_password


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "has_boarded": db_user.has_boarded,
        },
    }


class UserReset(BaseModel):
    email: EmailStr
    new_password: str


@router.post("/reset-password")
def reset_password(data: UserReset, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Email not found")

    db_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"status": "success", "message": "Password updated successfully"}


@router.post("/finish-onboarding/{user_id}")
def finish_onboarding(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.has_boarded = True
    db.commit()
    return {"message": "Onboarding finished"}


class GoogleLoginRequest(BaseModel):
    token: str
    email: str
    name: str


@router.post("/google")
def google_login(data: GoogleLoginRequest, db: Session = Depends(get_db)):
    # In a real app, we would verify the 'token' with Google API
    # For this project, we'll simulate the success if a valid-looking email is provided
    db_user = db.query(User).filter(User.email == data.email).first()

    if not db_user:
        # Create user if doesn't exist (Auto-signup for Google)
        db_user = User(
            full_name=data.name,
            email=data.email,
            hashed_password=get_password_hash(
                "google_oauth_placeholder"
            ),  # Dummy password
            has_boarded=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    return {
        "message": "Google login successful",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "has_boarded": db_user.has_boarded,
        },
    }


class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr


@router.put("/update-profile/{user_id}")
def update_profile(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.full_name = data.full_name
    db_user.email = data.email
    db.commit()
    db.refresh(db_user)

    return {
        "status": "success",
        "message": "Profile updated successfully",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "has_boarded": db_user.has_boarded,
        },
    }
