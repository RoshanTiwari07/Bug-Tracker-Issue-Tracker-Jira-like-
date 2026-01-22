from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.schemas.user import UserResponse

class CommentBase(BaseModel):
    """Base comment schema"""
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    parent_id: Optional[UUID] = None

class CommentResponse(CommentBase):
    id: UUID
    ticket_id: UUID
    author_id: UUID
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime    
    is_edited: bool

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class CommentWithAuthor(CommentResponse):
    """Comment response schema with author details"""
    author: UserResponse
    replies: List[CommentResponse]