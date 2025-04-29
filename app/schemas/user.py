from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    
class UserLoginGoogleRequest(BaseModel):
    id_token: str
    
class UserLoginGoogleResponse(BaseModel):
    message: str
    user_id:int

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
    email: EmailStr
    new_password: str
    
class PasswordVerifyConfirm(BaseModel):
    token: str
    email: str
