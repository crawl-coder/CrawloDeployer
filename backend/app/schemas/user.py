# /app/schemas/user.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    username: str
    password: str

    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserUpdateMe(BaseModel):
    """用户更新个人信息的模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserUpdatePassword(BaseModel):
    """用户更新密码的模型"""
    current_password: str
    new_password: str

    @field_validator('new_password')
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True