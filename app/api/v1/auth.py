from fastapi import APIRouter, Depends, Response, Request, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from app.schemas.user import *
from app.services import auth
from app.services import device
from app.db.session import get_db
from app.models.user import User
from app.models.device import Device
from app.core.security import get_current_user 
from typing import Annotated
from jose import jwt, JWTError
from app.utils.email import send_forgot_password_email
from app.utils.enums import OTPEnum

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup( background_tasks: BackgroundTasks, user: UserCreate, db: Session = Depends(get_db)):
   
    
    user = auth.register_user(db, user, background_tasks)
    
    return user
    

@router.post("/google-signup", response_model=UserLoginGoogleResponse)
def google_signup( background_tasks: BackgroundTasks, user: UserLoginGoogleRequest, response: Response, request: Request, db: Session = Depends(get_db),
    device_id: str = Header(None, alias="Device-ID"),
    mac_address: str = Header(None, alias="MAC-Address"),
    location: str = Header(None, alias="Location"),
                  ):
   
    
          
    # Assume `user_data` has been validated and contains email, password
    user = auth.google_signup(db, user, background_tasks)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Google Login")

    # Generate access and refresh tokens
    access_token = auth.create_access_token({"sub": user.id})
    refresh_token = auth.create_refresh_token({"sub": user.id})

    # Get device details (these would be in the request headers or custom headers)
    device_info = {
        "device_name": request.headers.get("User-Agent"),
        "device_id": device_id,
        "mac_address": mac_address,
        "ip_address": request.client.host,
        "location": location,
    }

    # Create or update device record
    device.create_or_update_device(db, user.id, device_info, refresh_token)

    # Set tokens in cookies
    response.set_cookie("access_token", access_token, httponly=True, max_age=1800, secure=True, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=86400, secure=True, samesite="lax")

    return {"message": "Login successful", "user_id": user.id}
    

@router.post("/login", response_model=Token)
def login(background_tasks: BackgroundTasks, user_data: UserLogin, response: Response, request: Request, db: Session = Depends(get_db),
          device_id: str = Header(None, alias="Device-ID"),
        mac_address: str = Header(None, alias="MAC-Address"),
    location: str = Header(None, alias="Location"),
          ):
    # Assume `user_data` has been validated and contains email, password
    user = auth.authenticate_user(db, email=user_data.email, password=user_data.password, background_tasks=background_tasks)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # if user and not user.is_verified:
    #     raise HTTPException(status_code=401, detail="Please verify your account")

    # Generate access and refresh tokens
    access_token = auth.create_access_token({"sub": user.id})
    refresh_token = auth.create_refresh_token({"sub": user.id})

    # Get device details (these would be in the request headers or custom headers)
    device_info = {
        "device_name": request.headers.get("User-Agent"),
        "device_id": device_id,
        "mac_address": mac_address,
        "ip_address": request.client.host,
        "location": location,
    }

    # Create or update device record
    device.create_or_update_device(db, user.id, device_info, refresh_token)

    # Set tokens in cookies
    response.set_cookie("access_token", access_token, httponly=True, max_age=1800, secure=True, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=86400, secure=True, samesite="lax")

    return {"message": "Login successful", "user_id": user.id}

@router.post("/forgot-password")
def forgot(background_tasks: BackgroundTasks, data: PasswordResetRequest, db: Session = Depends(get_db)):
    token = auth.generate_otp_code(db, data.email, OTPEnum.FORGOT, background_tasks)
  
    print(f"Reset link: https://yourapp.com/reset-password?token={token}")
    return {"message": "Reset link sent"}

@router.post("/verify-otp")
def verify(data: PasswordVerifyConfirm, db: Session = Depends(get_db)):
    auth.verify_code(db, data.token, data.email, data.token_type)
    return {"message": "Code verified successfully"}

@router.post("/reset-password")
def reset(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    auth.reset_password(db,data.email, data.token, data.new_password)
    return {"message": "Password updated successfully"}

@router.get("/profile")
def get_profile(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token, "refresh token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    # print(type(current_user), "current_user")
    # print(current_user, "current_user")
    # Set tokens in cookies
    
    token = device.refresh_tokens(db, refresh_token)
    print(token, "token")
    response.set_cookie("access_token", token["access_token"], httponly=True, max_age=1800, secure=True, samesite="lax")
    response.set_cookie("refresh_token", token["refresh_token"], httponly=True, max_age=86400, secure=True, samesite="lax")
    return {"message": "Token refreshed successfully"}

# Logout route
@router.post("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    user_id = device.verify_refresh_token(refresh_token)

    # Revoke the device's refresh token
    device.revoke_device(db, user_id)

    # Delete cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}
