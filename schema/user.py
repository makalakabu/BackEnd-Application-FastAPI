from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email:  EmailStr

class UserCreate(UserBase):
    password: str

class UserInformation(UserBase):
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True