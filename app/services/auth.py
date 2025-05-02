from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLoginGoogleRequest
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.utils.email import send_registration_email, send_forgot_password_email
import uuid
import random
from google.oauth2 import id_token
from pydantic import  EmailStr
from google.auth.transport import requests as grequests
from app.core.config import settings 
from typing import Literal
from app.utils.enums import OTPEnum

def register_user(db: Session, user: UserCreate, background_tasks: BackgroundTasks):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw, full_name=user.full_name)
    db.add(new_user)
    token = str(random.randint(100000, 999999)) 
    new_user.set_otp_token(token, OTPEnum.REGISTER)
    db.commit()
    db.refresh(new_user)
    
    bod = {
        'title': f"Verification for account",
        'name': {user.full_name},
        'code':  token
    }
    send_registration_email(background_tasks, user.email, bod)
    return new_user

def google_signup(db: Session, data: UserLoginGoogleRequest, background_tasks: BackgroundTasks):
    try:
        idinfo = id_token.verify_oauth2_token(
            data.id_token,
            grequests.Request(),
           settings.GOOGLE_CLIENT_ID
        )

        email = idinfo["email"]
        sub = idinfo["sub"]  # Google user ID
        name = idinfo.get("name")
        picture = idinfo.get("picture")
        
        print(email, "EMAIL")
        
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return existing
        
        new_user = User(email=email, hashed_password=None, full_name=name, provider="GOOGLE", provider_id=sub)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        bod = {
        'title': 'Hello World',
        'name': 'John Doe'
    }
        send_registration_email(background_tasks, new_user.email, bod)
        return new_user

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

def authenticate_user(db: Session, email: str, password: str, background_tasks: BackgroundTasks):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user and not user.is_verified:
        generate_otp_code(db, email, otp_type=OTPEnum.REGISTER, background_tasks=background_tasks)
        token = str(random.randint(100000, 999999)) 
        user.set_otp_token(token, OTPEnum.REGISTER)
        db.commit()
        bod = {
        'title': f"Verification for account",
        'name': {user.full_name},
        'code':  token
    }
        send_registration_email(background_tasks, user.email, bod)
        # raise HTTPException(status_code=401, detail="Please verify your account")
    
    return user

def generate_otp_token(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = str(uuid.uuid4())
    user.set_otp_token(token)
    db.commit()
    return token

def generate_otp_code(db: Session, email: str, otp_type:OTPEnum, background_tasks: BackgroundTasks):
    user = db.query(User).filter(User.email == email).first()
    print("user", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = str(random.randint(100000, 999999)) 
    user.set_otp_token(token, otp_type)
    db.commit()
    bod = {
        'title': f"Verification for account" if otp_type == OTPEnum.REGISTER else f"Verification for password reset",
        'name': {user.full_name},
        'code':  token
    }
    send_forgot_password_email(background_tasks, user.email, bod)
    return token

def verify_code(db: Session, token: str, email:str, type: OTPEnum):
    print(token, "token")
    user = db.query(User).filter(User.otp_token == token, User.email == email).first()
    print(user, "USER")
    if not user or not user.is_otp_token_expired():
        raise HTTPException(status_code=400, detail="OTP code is expired")
    
    if type == OTPEnum.REGISTER and not user.is_verified:
        user.is_verified = True
        db.commit()
        return True
    
    return True

def reset_password(db: Session, email:EmailStr, token:str, new_password: str):
    user = db.query(User).filter(User.email == email, User.otp_token == token).first()
    if not user or not user.is_otp_token_expired():
        raise HTTPException(status_code=400, detail="User not found")
    user.hashed_password = get_password_hash(new_password)
    user.otp_token = None
    user.otp_token_expiry = None
    user.otp_type = None
    db.commit()
    return True


