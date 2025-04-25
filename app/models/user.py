from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base  # SQLAlchemy base class
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    
    devices = relationship("Device", back_populates="user", uselist=True)  # Relationship with Device model

    def set_reset_token(self, token: str, expiry_minutes: int = 2):
        """Set the reset token with an expiration time."""
        self.reset_token = token
        self.reset_token_expiry = datetime.now() + timedelta(minutes=expiry_minutes)
    
    def is_reset_token_expired(self):
        """Check if the reset token has expired."""
        return self.reset_token_expiry and datetime.now() > self.reset_token_expiry