from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.db.base import Base  # SQLAlchemy base class
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from app.utils.enums import OTPEnum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    otp_token = Column(String, nullable=True)
    otp_token_expiry = Column(DateTime, nullable=True)
    otp_type = Column(Enum(OTPEnum, name="otp_enum", create_constraint=True), nullable=True )
    provider = Column(String, nullable=True)
    provider_id = Column(String, nullable=True)
    
    devices = relationship("Device", back_populates="user", uselist=True)  # Relationship with Device model

    def set_otp_token(self, token: str, otp_type: OTPEnum, expiry_minutes: int = 15):
        """Set the otp token with an expiration time."""
        self.otp_token = token
        self.otp_type = otp_type
        self.otp_token_expiry = datetime.now() + timedelta(minutes=expiry_minutes)
    
    def is_otp_token_expired(self):
        """Check if the otp token has expired."""
        return self.otp_token_expiry and datetime.now() < self.otp_token_expiry