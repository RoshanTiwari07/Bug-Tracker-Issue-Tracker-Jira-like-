from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.db.session import get_db
from app.models.user import User
from app.core.config import get_settings

settings = get_settings()

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/form")

# Database session dependency
SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Validates token and retrieves user from database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("id")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Query user from database
    try:
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
    except Exception:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure the current user is active.
    Use this for routes that require an active account.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Dependency to ensure the current user has admin role.
    Use this for admin-only routes.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


async def require_developer_or_admin(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    """
    Dependency to ensure the current user is developer or admin.
    Use this for routes that require elevated permissions.
    """
    if current_user.role not in ["admin", "developer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Developer or Admin access required."
        )
    return current_user


# Type annotations for easy use in routes
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_admin)]
DeveloperOrAdminUser = Annotated[User, Depends(require_developer_or_admin)]



