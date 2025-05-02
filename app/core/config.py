from pydantic import EmailStr  # For type-safe settings using environment variables
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str  # Connection string for the SQL database
    SECRET_KEY: str # Secret key for signing JWT tokens
    JWT_ALGORITHM: str = "HS256"  # Algorithm used for encoding JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # Token lifetime
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # Refresh Token lifetime
    EMAIL_FROM: EmailStr 
    SMTP_SERVER: str   # Outgoing email server
    SMTP_PORT: int = 465
    SMTP_USER: str 
    SMTP_PASSWORD: str
    GOOGLE_CLIENT_ID: str

    class Config:
        env_file = ".env"  # Load from .env

settings = Settings()
