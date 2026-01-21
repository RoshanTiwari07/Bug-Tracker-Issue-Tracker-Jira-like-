from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    """User role enum"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6, max_length=72)
    full_name: Optional[str] = None
    timezone: str = "UTC"


class UserRegister(UserCreate):
    """User registration response schema"""
    pass


class UserLogin(BaseModel):
    """User login request schema"""
    username_or_email: str  # Can be either email or username
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema (without sensitive data)"""
    id: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    timezone: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Authentication response with user and token"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
