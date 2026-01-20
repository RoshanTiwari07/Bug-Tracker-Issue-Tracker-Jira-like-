from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel, UniqueConstraint
from datetime import datetime


class Label(SQLModel, table=True):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="unique_label_per_project"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(nullable=False, foreign_key="projects.id")
    name: str = Field(max_length=50, nullable=False)  # "frontend", "urgent", "bug"
    color: str = Field(max_length=7, nullable=False)  # "#FF5733" (hex color)
    description: str = Field(max_length=255, nullable=True)
    
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.utcnow)
    )


class IssueLabel(SQLModel, table=True):
    __tablename__ = "issue_labels"
    __table_args__ = (
        UniqueConstraint("ticket_id", "label_id", name="unique_ticket_label"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(nullable=False, foreign_key="tickets.id")
    label_id: UUID = Field(nullable=False, foreign_key="labels.id")
    
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.utcnow)
    )