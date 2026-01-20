from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel
from datetime import datetime


class Activity(SQLModel, table=True):
    __tablename__ = "activities"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(nullable=False, foreign_key="tickets.id")
    user_id: UUID = Field(nullable=False, foreign_key="users.id")
    
    # What happened
    action: str = Field(max_length=50, nullable=False)  # "created", "updated", "commented", "assigned", "status_changed"
    
    # Change details
    field_changed: str = Field(max_length=50, nullable=True)  # "status", "assignee", "priority"
    old_value: str = Field(max_length=255, nullable=True)  # "todo"
    new_value: str = Field(max_length=255, nullable=True)  # "in_progress"
    
    # Optional extra data
    extra_data: str = Field(nullable=True)  # JSON string for extra data
    
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.utcnow)
    )