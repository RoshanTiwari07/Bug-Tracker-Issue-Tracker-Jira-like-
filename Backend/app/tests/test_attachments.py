import pytest
from uuid import uuid4
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile

from app.services.attachment_service import AttachmentService
from app.models.attachment import Attachment
from app.models.ticket import Ticket
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_upload_attachment_success(db: AsyncSession):
    """Test successful file upload"""
    # Create service
    service = AttachmentService(db)
    
    # Create mock user and ticket
    user_id = uuid4()
    ticket_id = uuid4()
    
    # Mock database get calls
    db.get = AsyncMock()
    db.get.side_effect = [
        Ticket(id=ticket_id, project_id=uuid4(), reporter_id=user_id),  # First call for ticket
        User(id=user_id, username="test", email="test@example.com")  # Second call for user
    ]
    
    # Create mock file
    file = AsyncMock(spec=UploadFile)
    file.filename = "test_document.pdf"
    file.content_type = "application/pdf"
    file.size = 1024 * 100  # 100 KB
    file.read = AsyncMock(return_value=b"test content")
    
    # Mock the file saving
    with patch.object(service, '_save_file', new_callable=AsyncMock) as mock_save:
        mock_save.return_value = "uploads/attachments/test_uuid.pdf"
        
        # Mock database add
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        
        # Call the method
        result = await service.upload_attachment(ticket_id, user_id, file)
        
        # Verify the result
        assert result.filename == "test_uuid.pdf"
        assert result.original_filename == "test_document.pdf"
        assert result.mime_type == "application/pdf"


@pytest.mark.asyncio
async def test_upload_attachment_file_too_large(db: AsyncSession):
    """Test upload with file exceeding size limit"""
    service = AttachmentService(db)
    
    # Create mock file with large size
    file = AsyncMock(spec=UploadFile)
    file.filename = "large_file.pdf"
    file.content_type = "application/pdf"
    file.size = 100 * 1024 * 1024  # 100 MB (exceeds 50 MB limit)
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="exceeds maximum allowed size"):
        await service._validate_file(file)


@pytest.mark.asyncio
async def test_upload_attachment_invalid_type(db: AsyncSession):
    """Test upload with invalid file type"""
    service = AttachmentService(db)
    
    # Create mock file with invalid type
    file = AsyncMock(spec=UploadFile)
    file.filename = "malware.exe"
    file.content_type = "application/x-msdownload"
    file.size = 1024
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="not allowed"):
        await service._validate_file(file)


@pytest.mark.asyncio
async def test_get_ticket_attachments(db: AsyncSession):
    """Test retrieving all attachments for a ticket"""
    service = AttachmentService(db)
    
    ticket_id = uuid4()
    
    # Mock database get
    db.get = AsyncMock(return_value=Ticket(id=ticket_id, project_id=uuid4(), reporter_id=uuid4()))
    
    # Mock query execution
    attachments = [
        Attachment(id=uuid4(), ticket_id=ticket_id, uploaded_by=uuid4(), filename="test1.pdf", original_filename="file1.pdf", file_path="/path/to/file1.pdf", file_size=1024, mime_type="application/pdf"),
        Attachment(id=uuid4(), ticket_id=ticket_id, uploaded_by=uuid4(), filename="test2.pdf", original_filename="file2.pdf", file_path="/path/to/file2.pdf", file_size=2048, mime_type="application/pdf"),
    ]
    
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = attachments
    db.execute = AsyncMock(return_value=mock_result)
    
    # Call the method
    result = await service.get_ticket_attachments(ticket_id)
    
    # Verify
    assert len(result) == 2


@pytest.mark.asyncio
async def test_delete_attachment_by_owner(db: AsyncSession):
    """Test attachment deletion by owner"""
    service = AttachmentService(db)
    
    attachment_id = uuid4()
    user_id = uuid4()
    
    attachment = Attachment(
        id=attachment_id,
        ticket_id=uuid4(),
        uploaded_by=user_id,
        filename="test.pdf",
        original_filename="document.pdf",
        file_path="uploads/attachments/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    # Mock database get
    db.get = AsyncMock(return_value=attachment)
    
    # Mock file deletion
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.unlink'):
        
        # Mock database delete
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        
        # Call the method
        result = await service.delete_attachment(attachment_id, user_id, is_admin=False)
        
        # Verify
        assert result is True
        db.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_attachment_permission_denied(db: AsyncSession):
    """Test deletion permission check"""
    service = AttachmentService(db)
    
    attachment_id = uuid4()
    user_id = uuid4()
    other_user_id = uuid4()
    
    attachment = Attachment(
        id=attachment_id,
        ticket_id=uuid4(),
        uploaded_by=other_user_id,  # Different user
        filename="test.pdf",
        original_filename="document.pdf",
        file_path="uploads/attachments/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    # Mock database get
    db.get = AsyncMock(return_value=attachment)
    
    # Should raise PermissionError
    with pytest.raises(PermissionError, match="only delete your own attachments"):
        await service.delete_attachment(attachment_id, user_id, is_admin=False)


@pytest.mark.asyncio
async def test_delete_attachment_by_admin(db: AsyncSession):
    """Test attachment deletion by admin"""
    service = AttachmentService(db)
    
    attachment_id = uuid4()
    user_id = uuid4()
    other_user_id = uuid4()
    
    attachment = Attachment(
        id=attachment_id,
        ticket_id=uuid4(),
        uploaded_by=other_user_id,
        filename="test.pdf",
        original_filename="document.pdf",
        file_path="uploads/attachments/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    # Mock database get
    db.get = AsyncMock(return_value=attachment)
    
    # Mock file deletion
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.unlink'):
        
        # Mock database delete
        db.delete = AsyncMock()
        db.commit = AsyncMock()
        
        # Call the method with admin flag
        result = await service.delete_attachment(attachment_id, user_id, is_admin=True)
        
        # Verify
        assert result is True
        db.delete.assert_called_once()
