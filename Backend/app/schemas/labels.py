from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID



class LabelBase(BaseModel):
    """Base label schema"""
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, regex="^#(?:[0-9a-fA-F]{3}){1,2}$")  
    description: Optional[str] = None

class LabelCreate(LabelBase):
    """Label creation schema"""
    pass

class LabelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, regex="^#(?:[0-9a-fA-F]{3}){1,2}$")
    description: Optional[str] = None

class LabelResponse(LabelBase):
    id: UUID
    project_id: UUID
    created_at: datetime

class IssueLabelCreate(BaseModel):
    label_id: UUID

class IssueLabelResponse(BaseModel):
    id:UUID
    ticket_id: UUID
    label_id: UUID
    label: LabelResponse
    created_at: datetime