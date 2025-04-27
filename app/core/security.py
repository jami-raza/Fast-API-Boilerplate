from datetime import datetime, timedelta
from jose import jwt, JWTError  # For encoding and decoding JWT tokens
from passlib.context import CryptContext  # Password hashing
from app.core.config import settings  # App settings
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.device import Device
from typing import Annotated

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Bcrypt hashing context
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # Define the OAuth2PasswordBearer for access token extraction

# Utility to get the current time for token expiration
def get_refresh_token_expiration():
    return datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

def get_password_hash(password):
    return pwd_context.hash(password)  # Hash the plain password

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)  # Compare passwords

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Ensure "sub" is string (required for decoding later)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> tuple:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    
    # Ensure "sub" is string (required for decoding later)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


security = HTTPBearer()

def get_current_user(request: Request, response: Response):
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    print(access_token, "access_token")
    if not refresh_token or not access_token:
        raise HTTPException(status_code=401, detail="Missing access or refresh token")
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return {"user_id": payload.get("sub")}

    # except jwt.ExpiredSignatureError:
    #     # Try refresh token
    #     try:
    #         payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    #         user_id = payload.get("sub")

    #         # Re-issue tokens
    #         new_access = create_access_token({"sub": user_id})
    #         new_refresh = create_refresh_token({"sub": user_id})

    #         response.set_cookie("access_token", new_access, httponly=True, max_age=1800, secure=True, samesite="lax")
    #         response.set_cookie("refresh_token", new_refresh, httponly=True, max_age=86400, secure=True, samesite="lax")

    #         return {"user_id": user_id}

    #     except jwt.ExpiredSignatureError:
    #         raise HTTPException(status_code=401, detail="Refresh token expired")
    #     except jwt.JWTError:
    #         raise HTTPException(status_code=401, detail="Invalid refresh token")

    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
# Decode refresh token
def decode_refresh_token(refresh_token: str):
    try:
        print(refresh_token, "refresh_token decode")
        print(f"Refresh token length: {len(refresh_token)}")
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(payload, "refresh_token decode payload")
        
        return payload
    except JWTError as e:
        print(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    

