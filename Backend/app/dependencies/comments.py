from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.comment_service import CommentService

SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_comment_service(db: SessionDep) -> CommentService:
    """Dependency to provide CommentService instance"""
    return CommentService(db)


CommentServiceDep = Annotated[CommentService, Depends(get_comment_service)]
