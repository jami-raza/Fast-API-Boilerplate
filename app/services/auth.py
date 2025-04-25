from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
import uuid

def register_user(db: Session, user: UserCreate):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def generate_reset_token(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = str(uuid.uuid4())
    user.set_reset_token(token)
    db.commit()
    return token

def reset_password(db: Session, token: str, new_password: str):
    user = db.query(User).filter(User.reset_token == token).first()
    if not user or not user.is_reset_token_expired():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db.commit()
    return True


