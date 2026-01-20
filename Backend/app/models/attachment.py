from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel
from datetime import datetime


class Attachment(SQLModel, table=True):
    __tablename__ = "attachments"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(nullable=False, foreign_key="tickets.id")
    uploaded_by: UUID = Field(nullable=False, foreign_key="users.id")
    
    # File info
    filename: str = Field(max_length=255, nullable=False)
    original_filename: str = Field(max_length=255, nullable=False)
    file_path: str = Field(max_length=500, nullable=False)
    file_url: str = Field(max_length=500, nullable=True)  # CDN URL if using cloud storage
    
    # Metadata
    file_size: int = Field(nullable=False)  # Size in bytes
    mime_type: str = Field(max_length=100, nullable=False)  # "image/png", "application/pdf"
    
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow)
    )