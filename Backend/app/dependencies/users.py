from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user_service import UserService


async def get_user_service(
    session: AsyncSession = Depends(get_db)
) -> UserService:
    """Get user service with database session"""
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
