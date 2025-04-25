from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base  # replace with your actual Base import


class Device(Base):
    __tablename__ = "devices"

    token = Column(String, primary_key=True, index=True)  # Refresh token
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_name = Column(String)
    device_id = Column(String, index=True)  # e.g., fingerprinted browser/device ID
    mac_address = Column(String)
    ip_address = Column(String)
    location = Column(String)
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="devices")  # Optional if using User relationship
