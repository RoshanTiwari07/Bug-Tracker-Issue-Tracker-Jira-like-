from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field
from enum import Enum
from datetime import datetime
from app.db.base import BaseModel
from app.db.types import role_enum

class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    

class User(BaseModel, table = True):
    __tablename__ = "users"

    full_name : str = Field(nullable=True)
    avatar_url : str = Field(nullable=True)
    role: UserRole = Field(sa_column=Column(role_enum, nullable=False), default=UserRole.DEVELOPER)
    timezone: str = Field(default="UTC", nullable=False)
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow, onupdate=datetime.utcnow) 
    )
    last_login: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, nullable=True)    
    )


    