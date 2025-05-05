import requests
from datetime import datetime
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.device import Device
from app.core.security import create_access_token, create_refresh_token, get_refresh_token_expiration, decode_refresh_token  # Assuming you have these in a utils file
from app.core.config import settings


def get_ip_and_location(request):
    # Get client IP
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.client.host

    # Get location from IP
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}")
        data = res.json()
        location = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
    except Exception:
        location = "Unknown"

    return ip, location


def rotate_refresh_token(old_token: str, request, response, db: Session):
    # Decode old token
    try:
        payload = jwt.decode(old_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Validate in DB
    device = db.query(Device).filter(Device.token == old_token, Device.revoked == False).first()
    if not device or device.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Expired or revoked refresh token")

    # Revoke old
    device.revoked = True
    db.commit()

    # Generate new tokens
    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token, expires_at = create_refresh_token({"sub": user_id})

    # Get IP and location
    ip, location = get_ip_and_location(request)

    # Save new token
    new_device = Device(
        token=new_refresh_token,
        user_id=user_id,
        device_name=device.device_name,
        device_id=device.device_id,
        ip_address=ip,
        location=location,
        expires_at=expires_at,
    )
    db.add(new_device)
    db.commit()

    # Set new cookies
    response.set_cookie("access_token", new_access_token, httponly=True, max_age=1800, secure=True, samesite="lax")
    response.set_cookie("refresh_token", new_refresh_token, httponly=True, max_age=604800, secure=True, samesite="lax")

    return {"message": "Token refreshed"}

# Create a new device or update existing one
def create_or_update_device(db: Session, user_id: str, device_info: dict, refresh_token: str):
    device_id = device_info.get("device_id")
    device = db.query(Device).filter(Device.device_id == device_id, Device.user_id == user_id).first()

    if device:
        # Update the device if it exists
        device.token = refresh_token
        device.expires_at = get_refresh_token_expiration()
        device.revoked = False  # Device is no longer revoked
    else:
        # Create new device record
        new_device = Device(
            user_id=user_id,
            device_name=device_info.get("device_name"),
            device_id=device_id,
            mac_address=device_info.get("mac_address"),
            ip_address=device_info.get("ip_address"),
            location=device_info.get("location"),
            token=refresh_token,
            expires_at=get_refresh_token_expiration(),
        )
        db.add(new_device)
    
    db.commit()

# Refresh tokens for the user
def refresh_tokens(db: Session, refresh_token:str):
    
    user_id = verify_refresh_token(refresh_token)
    
    # Generate new access and refresh tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    # Update the device's refresh token and expiration
    device = db.query(Device).filter(Device.user_id == user_id).first()
    if device and device.revoked != True:
        device.token = refresh_token
        device.expires_at = get_refresh_token_expiration()
        db.commit()

    return {"access_token":access_token, "refresh_token":refresh_token}

# Revoke a device's refresh token
def revoke_device(db: Session, user_id: str):
    device = db.query(Device).filter(Device.user_id == user_id).first()
    if device:
        device.revoked = True  # Set device token to revoked
        db.commit()

# Verify if a refresh token is valid
def verify_refresh_token(refresh_token: str):
    try:
        print(refresh_token, "refresh_token")
        # Decode and verify the refresh token
        payload = decode_refresh_token(refresh_token)
        return payload.get("sub")
    except JWTError as e:
        print(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
