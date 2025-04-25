from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True  # Enable ORM serialization

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    # access_token: str
    # refresh_token: str
    message: str
    user_id:int

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
