"""
Attachments API - Clean, production-level file upload and management
All file operations delegated to services.
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List
from uuid import UUID
import logging

from app.dependencies.auth import CurrentActiveUser, SessionDep
from app.dependencies.attachments import AttachmentServiceDep
from app.schemas.attachment import AttachmentResponse, AttachmentWithUploader
from app.models.user import User
from app.models.ticket import Ticket
from app.utils.router_helpers import ErrorHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/attachments", tags=["attachments"])

# ============= HELPERS =============

async def _verify_ticket_exists(ticket_id: UUID, db: SessionDep) -> Ticket:
    """Helper to verify ticket exists"""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise ErrorHandler.handle_not_found("Ticket")
    return ticket


# ============= ENDPOINTS =============

@router.post("/tickets/{ticket_id}/upload", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: UUID,
    file: UploadFile,
    current_user: CurrentActiveUser,
    service: AttachmentServiceDep,
    db: SessionDep
):
    """Upload a file attachment to a ticket"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        attachment = await service.upload_attachment(
            ticket_id=ticket_id,
            uploaded_by=current_user.id,
            file=file
        )
        
        return AttachmentResponse.model_validate(attachment)
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except PermissionError as e:
        raise ErrorHandler.handle_permission_denied(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload attachment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/tickets/{ticket_id}/attachments", response_model=List[AttachmentWithUploader])
async def list_ticket_attachments(
    ticket_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser,
    service: AttachmentServiceDep,
    skip: int = 0,
    limit: int = 50
):
    """Get all attachments for a ticket"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        attachments = await service.get_ticket_attachments(
            ticket_id=ticket_id,
            skip=skip,
            limit=limit
        )
        
        # Enrich with uploader details
        enriched = []
        for attachment in attachments:
            uploader = await db.get(User, attachment.uploaded_by)
            enriched.append(AttachmentWithUploader(
                **attachment.__dict__,
                uploader=uploader
            ))
        
        return enriched
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list attachments: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/{attachment_id}", response_model=AttachmentWithUploader)
async def get_attachment(
    attachment_id: UUID,
    current_user: CurrentActiveUser,
    service: AttachmentServiceDep,
    db: SessionDep
):
    """Get a specific attachment"""
    try:
        attachment = await service.get_attachment(attachment_id)
        if not attachment:
            raise ErrorHandler.handle_not_found("Attachment")
        
        uploader = await db.get(User, attachment.uploaded_by)
        
        return AttachmentWithUploader(
            **attachment.__dict__,
            uploader=uploader
        )
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get attachment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: UUID,
    current_user: CurrentActiveUser,
    service: AttachmentServiceDep
):
    """Download an attachment file"""
    try:
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        file_path = await service.get_file_path(attachment_id)
        
        return FileResponse(
            path=file_path,
            filename=Path(file_path).name,
            media_type="application/octet-stream"
        )
    except ValueError as e:
        raise ErrorHandler.handle_not_found("Attachment")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download attachment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: UUID,
    current_user: CurrentActiveUser,
    service: AttachmentServiceDep,
    db: SessionDep
):
    """Delete an attachment (uploader only)"""
    try:
        await service.delete_attachment(
            attachment_id=attachment_id,
            user_id=current_user.id,
            is_admin=False
        )
    except ValueError as e:
        raise ErrorHandler.handle_not_found("Attachment")
    except PermissionError as e:
        raise ErrorHandler.handle_permission_denied(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete attachment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/user/me/attachments", response_model=List[AttachmentWithUploader])
async def list_my_attachments(
    current_user: CurrentActiveUser,
    service: AttachmentServiceDep,
    db: SessionDep,
    skip: int = 0,
    limit: int = 50
):
    """Get all attachments uploaded by current user"""
    try:
        attachments = await service.get_user_attachments(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        enriched = []
        for attachment in attachments:
            uploader = await db.get(User, attachment.uploaded_by)
            enriched.append(AttachmentWithUploader(
                **attachment.__dict__,
                uploader=uploader
            ))
        
        return enriched
    except Exception as e:
        logger.error(f"Failed to list user attachments: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()
