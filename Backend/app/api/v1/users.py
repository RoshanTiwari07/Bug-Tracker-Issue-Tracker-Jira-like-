from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from app.dependencies.auth import CurrentActiveUser, SessionDep
from app.dependencies.users import UserServiceDep
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserServiceDep = None
):
    """Create a new user (public endpoint for registration)"""
    try:
        user = await service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: CurrentActiveUser = None
):
    """Get current authenticated user's profile"""
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None
):
    """Get user by ID (accessible to authenticated users)"""
    try:
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_validate(user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None,
    skip: int = 0,
    limit: int = 50
):
    """Get all users with pagination"""
    try:
        users = await service.get_all_users(skip=skip, limit=limit)
        return [UserResponse.model_validate(user) for user in users]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None
):
    """Update current user's profile"""
    try:
        user = await service.update_user(current_user.id, update_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None
):
    """Update a user (admin only)"""
    try:
        # Check if user is admin
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update other users"
            )
        
        user = await service.update_user(user_id, update_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e) else status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None
):
    """Delete a user (admin only)"""
    try:
        # Check if user is admin
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users"
            )
        
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account"
            )
        
        await service.delete_user(user_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None
):
    """Activate a user (admin only)"""
    try:
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can activate users"
            )
        
        user = await service.toggle_user_active(user_id, True)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    current_user: CurrentActiveUser = None,
    service: UserServiceDep = None
):
    """Deactivate a user (admin only)"""
    try:
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can deactivate users"
            )
        
        # Prevent self-deactivation
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        
        user = await service.toggle_user_active(user_id, False)
        return UserResponse.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )
