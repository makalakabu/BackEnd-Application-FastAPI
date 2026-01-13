import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class UserPublic(BaseModel):
    username: str
    email: EmailStr
    bio: str | None = None
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserProfile(UserPublic):
    followers_count: int
    following_count: int


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class UserInformation(UserPublic):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInTweet(BaseModel):
    username: str
    image: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    image: str | None = None
    bio: str | None = None
    is_private: bool | None = None

    model_config = ConfigDict(extra="forbid")