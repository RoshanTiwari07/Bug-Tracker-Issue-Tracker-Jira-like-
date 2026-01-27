from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.attachment_service import AttachmentService


async def get_attachment_service(
    session: AsyncSession = Depends(get_db)
) -> AttachmentService:
    """Get attachment service with database session"""
    return AttachmentService(session)


AttachmentServiceDep = Annotated[AttachmentService, Depends(get_attachment_service)]
