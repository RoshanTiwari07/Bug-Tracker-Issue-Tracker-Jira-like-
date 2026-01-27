from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List
from uuid import UUID
from pathlib import Path

from app.dependencies.auth import CurrentActiveUser, SessionDep
from app.dependencies.attachments import AttachmentServiceDep
from app.schemas.attachment import AttachmentResponse, AttachmentWithUploader
from app.models.user import User
from app.models.ticket import Ticket

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.post("/tickets/{ticket_id}/upload", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: UUID,
    file: UploadFile = File(...),
    current_user: CurrentActiveUser = None,
    service: AttachmentServiceDep = None,
    db: SessionDep = None
):
    """Upload a file attachment to a ticket"""
    try:
        # Verify ticket exists and user has access
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Upload attachment
        attachment = await service.upload_attachment(
            ticket_id=ticket_id,
            uploaded_by=current_user.id,
            file=file
        )
        
        return AttachmentResponse.model_validate(attachment)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload attachment: {str(e)}"
        )


@router.get("/tickets/{ticket_id}/attachments", response_model=List[AttachmentWithUploader])
async def list_ticket_attachments(
    ticket_id: UUID,
    current_user: CurrentActiveUser = None,
    service: AttachmentServiceDep = None,
    db: SessionDep = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all attachments for a ticket"""
    try:
        # Verify ticket exists
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Get attachments
        attachments = await service.get_ticket_attachments(
            ticket_id=ticket_id,
            skip=skip,
            limit=limit
        )
        
        # Enrich with uploader details
        enriched_attachments = []
        for attachment in attachments:
            uploader = await db.get(User, attachment.uploaded_by)
            attachment_dict = AttachmentResponse.model_validate(attachment).model_dump()
            attachment_dict["uploader"] = uploader
            enriched_attachments.append(attachment_dict)
        
        return enriched_attachments
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attachments"
        )


@router.get("/{attachment_id}", response_model=AttachmentWithUploader)
async def get_attachment(
    attachment_id: UUID,
    current_user: CurrentActiveUser = None,
    service: AttachmentServiceDep = None,
    db: SessionDep = None
):
    """Get a specific attachment"""
    try:
        # Get attachment
        attachment = await service.get_attachment(attachment_id)
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )
        
        # Get uploader info
        uploader = await db.get(User, attachment.uploaded_by)
        
        attachment_dict = AttachmentResponse.model_validate(attachment).model_dump()
        attachment_dict["uploader"] = uploader
        
        return attachment_dict
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attachment"
        )


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: UUID,
    current_user: CurrentActiveUser = None,
    service: AttachmentServiceDep = None
):
    """Download an attachment file"""
    try:
        # Get file path
        file_path = await service.get_file_path(attachment_id)
        
        # Return file for download
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=Path(file_path).name,
            media_type="application/octet-stream"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download attachment"
        )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: UUID,
    current_user: CurrentActiveUser = None,
    service: AttachmentServiceDep = None,
    db: SessionDep = None
):
    """Delete an attachment"""
    try:
        # Check if user is admin
        user = await db.get(current_user.__class__, current_user.id)
        is_admin = getattr(user, 'is_admin', False)
        
        # Delete attachment
        await service.delete_attachment(
            attachment_id=attachment_id,
            user_id=current_user.id,
            is_admin=is_admin
        )
        
        return None
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete attachment"
        )


@router.get("/user/me/attachments", response_model=List[AttachmentWithUploader])
async def list_my_attachments(
    current_user: CurrentActiveUser = None,
    service: AttachmentServiceDep = None,
    db: SessionDep = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all attachments uploaded by current user"""
    try:
        # Get user's attachments
        attachments = await service.get_user_attachments(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        # Enrich with uploader details
        enriched_attachments = []
        for attachment in attachments:
            uploader = await db.get(User, attachment.uploaded_by)
            attachment_dict = AttachmentResponse.model_validate(attachment).model_dump()
            attachment_dict["uploader"] = uploader
            enriched_attachments.append(attachment_dict)
        
        return enriched_attachments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attachments"
        )
