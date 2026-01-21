from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ProjectRole(str, Enum):
    """Project role enum"""
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=100)
    key: str = Field(..., min_length=2, max_length=10, pattern="^[A-Z0-9]+$")
    description: Optional[str] = None
    is_private: bool = True


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_private: Optional[bool] = None
    is_archived: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: UUID
    is_archived: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectMemberBase(BaseModel):
    """Base project member schema"""
    user_id: UUID
    role: ProjectRole = ProjectRole.DEVELOPER


class ProjectMemberAdd(BaseModel):
    """Add member to project schema"""
    user_id: UUID
    role: ProjectRole = ProjectRole.DEVELOPER


class ProjectMemberUpdate(BaseModel):
    """Update project member role"""
    role: ProjectRole


class ProjectMemberResponse(BaseModel):
    """Project member response schema"""
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    joined_at: datetime
    added_by: UUID
    
    class Config:
        from_attributes = True


class ProjectWithMembers(ProjectResponse):
    """Project with members list"""
    members: List[ProjectMemberResponse] = []
