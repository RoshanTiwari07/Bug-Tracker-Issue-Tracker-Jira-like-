import os
import shutil
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from pathlib import Path

from app.services.base import BaseService
from app.models.attachment import Attachment
from app.models.ticket import Ticket
from app.models.user import User


class AttachmentService(BaseService):
    """Attachment service for file upload/download logic"""
    
    # Configuration
    UPLOAD_DIR = Path("uploads/attachments")
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_MIME_TYPES = {
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv"
    }
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Attachment
        # Create upload directory if it doesn't exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    async def upload_attachment(
        self,
        ticket_id: UUID,
        uploaded_by: UUID,
        file: UploadFile
    ) -> Attachment:
        """Upload a file attachment to a ticket"""
        
        # Verify ticket exists
        ticket = await self.session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found")
        
        # Verify user exists
        user = await self.session.get(User, uploaded_by)
        if not user:
            raise ValueError(f"User '{uploaded_by}' not found")
        
        # Validate file
        await self._validate_file(file)
        
        # Save file to disk
        file_path = await self._save_file(file)
        
        # Create attachment record
        attachment = Attachment(
            ticket_id=ticket_id,
            uploaded_by=uploaded_by,
            filename=Path(file_path).name,
            original_filename=file.filename,
            file_path=file_path,
            file_url=f"/api/v1/attachments/{file_path.split('/')[-1]}/download",
            file_size=file.size,
            mime_type=file.content_type
        )
        
        return await self._add(attachment)
    
    async def get_attachment(self, attachment_id: UUID) -> Optional[Attachment]:
        """Get attachment by ID"""
        return await self._get(attachment_id)
    
    async def get_ticket_attachments(
        self,
        ticket_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Attachment]:
        """Get all attachments for a ticket"""
        
        # Verify ticket exists
        ticket = await self.session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found")
        
        query = select(Attachment).where(
            Attachment.ticket_id == ticket_id
        ).order_by(Attachment.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def delete_attachment(
        self,
        attachment_id: UUID,
        user_id: UUID,
        is_admin: bool = False
    ) -> bool:
        """Delete an attachment (by uploader or admin)"""
        
        attachment = await self._get(attachment_id)
        if not attachment:
            raise ValueError(f"Attachment '{attachment_id}' not found")
        
        # Check permissions
        if attachment.uploaded_by != user_id and not is_admin:
            raise PermissionError("You can only delete your own attachments")
        
        # Delete file from disk
        try:
            file_path = Path(attachment.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            raise ValueError(f"Failed to delete file: {str(e)}")
        
        # Delete attachment record
        await self._delete(attachment)
        return True
    
    async def get_file_path(self, attachment_id: UUID) -> Optional[str]:
        """Get file path for download"""
        attachment = await self._get(attachment_id)
        if not attachment:
            raise ValueError(f"Attachment '{attachment_id}' not found")
        
        file_path = Path(attachment.file_path)
        if not file_path.exists():
            raise ValueError("File not found on disk")
        
        return attachment.file_path
    
    async def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        
        # Check file size
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE / (1024*1024):.0f}MB")
        
        # Check MIME type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"File type '{file.content_type}' is not allowed")
        
        # Check filename
        if not file.filename:
            raise ValueError("Filename is required")
    
    async def _save_file(self, file: UploadFile) -> str:
        """Save uploaded file to disk and return path"""
        
        # Generate unique filename
        from uuid import uuid4
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid4()}{file_extension}"
        file_path = self.UPLOAD_DIR / unique_filename
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return str(file_path)
        except Exception as e:
            raise ValueError(f"Failed to save file: {str(e)}")
    
    async def get_user_attachments(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Attachment]:
        """Get all attachments uploaded by a user"""
        
        query = select(Attachment).where(
            Attachment.uploaded_by == user_id
        ).order_by(Attachment.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
