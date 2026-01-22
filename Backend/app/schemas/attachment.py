from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from Backend.app.schemas.user import UserResponse


class AttachmentResponse(BaseModel):
    """Attachment response schema"""
    id: UUID
    ticket_id: UUID
    uploaded_by: UUID
    filename: str
    original_filename: str
    file_size: int
    file_url: str
    created_at: datetime
    mime_type: str


class AttachmentWithUploader(AttachmentResponse):
    """Attachment response schema with uploader info"""
    uploader: UserResponse