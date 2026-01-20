from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import Field
from typing import Optional
Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Authentication fields
    email: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)