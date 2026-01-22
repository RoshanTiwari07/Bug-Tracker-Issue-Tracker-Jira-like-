from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel
from datetime import datetime, timezone
from app.db.types import issue_type_enum, issuestatus_enum, resolution_enum, priority_enum
from enum import Enum

class IssueType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"

class Status(str, Enum):
    IDEA = "idea"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"

class Resolution(str, Enum):
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"
    INCOMPLETE = "incomplete"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Ticket(SQLModel, table=True):
    model_config = {"arbitrary_types_allowed": True}
    __tablename__ = "tickets"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(max_length=15, unique=True, nullable=False, index=True)
    project_id: UUID = Field(nullable=False, foreign_key="projects.id")
    type: IssueType = Field(sa_column=Column(issue_type_enum, nullable=False))
    status: Status = Field(sa_column=Column(issuestatus_enum, nullable=False), default=Status.TODO)
    due_date: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), nullable=True)
    )
    resolution: Resolution = Field(sa_column=Column(resolution_enum, nullable=True))
    assignee_id: UUID = Field(nullable=True, foreign_key="users.id")
    is_archived: bool = Field(default=False, nullable=False)
    reporter_id: UUID = Field(nullable=False, foreign_key="users.id")
    priority: Priority = Field(sa_column=Column(priority_enum, nullable=False), default=Priority.MEDIUM)
    title: str = Field(nullable=False)
    description: str = Field(nullable=True)
    order_index: float = Field(default=0, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    )
    updated_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    )
    resolved_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP(timezone=True), nullable=True)
    )