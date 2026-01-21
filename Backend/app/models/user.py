from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel
from enum import Enum
from datetime import datetime, timezone
from uuid import uuid4, UUID
from app.db.types import role_enum
from typing import Optional

class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    

class User(SQLModel, table=True):
    __tablename__ = "users"

    # Primary Key
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    
    # Authentication fields (from BaseModel)
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    
    # Profile fields
    full_name: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)
    role: UserRole = Field(sa_column=Column(role_enum, nullable=False), default=UserRole.DEVELOPER)
    timezone: str = Field(default="UTC", nullable=False)
    
    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    )
    last_login: Optional[datetime] = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), nullable=True)
    )

    