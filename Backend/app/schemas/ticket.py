from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class statuses(str, Enum):
    """Ticket status options"""
    IN_PROGRESS = "in_progress"
    CANCELLED = "cancelled"
    DONE = "done"
    IN_REVIEW = "in_review"
    TODO = "todo"

class PriorityLevel(str, Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class issuetypes(str, Enum):
    """Ticket issue types"""
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"
    IMPROVEMENT = "improvement"

class Resolution(str, Enum):
    """Ticket resolution types"""
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"
    INCOMPLETE = "incomplete"

class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: issuetypes = issuetypes.TASK
    priority: PriorityLevel = PriorityLevel.MEDIUM
    due_date: Optional[datetime] = None

class TicketCreate(TicketBase):
    project_id: UUID
    assignee_id: Optional[UUID] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[issuetypes] = None
    priority: Optional[PriorityLevel] = None
    assignee_id: Optional[UUID] = None
    resolution: Optional[Resolution] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None

class TicketResponse(TicketBase):
    id: UUID
    key: str
    project_id: UUID
    status: statuses
    resolution: Optional[Resolution] = None
    assignee_id: Optional[UUID] = None
    reporter_id: UUID
    order_index: float
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
