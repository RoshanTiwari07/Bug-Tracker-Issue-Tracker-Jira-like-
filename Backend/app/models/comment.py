from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel
from datetime import datetime


class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(nullable=False, foreign_key="tickets.id")
    author_id: UUID = Field(nullable=False, foreign_key="users.id")
    parent_id: UUID = Field(nullable=True, foreign_key="comments.id")
    content: str = Field(nullable=False)
    is_edited: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow, onupdate=datetime.utcnow)
    )