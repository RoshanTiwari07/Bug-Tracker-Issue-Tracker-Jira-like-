"""
Authentication API - Clean production-level auth endpoints
All auth logic delegated to AuthService.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
import logging

from app.db.session import SessionDep
from app.dependencies.auth import CurrentActiveUser
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, AuthResponse
from app.utils.router_helpers import ErrorHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: SessionDep,
    background_tasks: BackgroundTasks
):
    """
    Register a new user account.
    - **email**: Valid email address (must be unique)
    - **username**: Username (must be unique)
    - **password**: Password (minimum 6 characters)
    - **full_name**: Optional full name
    - **timezone**: User timezone (default: UTC)
    """
    try:
        auth_service = AuthService(User, db, background_tasks)
        user, token = await auth_service._add_user(user_data.model_dump())
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=token,
            token_type="bearer"
        )
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except Exception as e:
        logger.error(f"Registration error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error("Failed to create user account")


@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: UserLogin,
    db: SessionDep,
    background_tasks: BackgroundTasks
):
    """
    Login with email or username and password.
    - **username_or_email**: User's email or username
    - **password**: User's password
    
    Returns user data and access token.
    """
    try:
        auth_service = AuthService(User, db, background_tasks)
        user, token = await auth_service.login_user(
            username_or_email=login_data.username_or_email,
            password=login_data.password
        )
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=token,
            token_type="bearer"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Login error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error("Login failed")


@router.post("/login/form", response_model=AuthResponse)
async def login_with_form(
    db: SessionDep,
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login endpoint compatible with OAuth2 password flow.
    Used by Swagger UI and other OAuth2 clients.
    - **username**: User's email or username
    - **password**: User's password
    """
    try:
        auth_service = AuthService(User, db, background_tasks)
        user, token = await auth_service.login_user(
            username_or_email=form_data.username,
            password=form_data.password
        )
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=token,
            token_type="bearer"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Login form error: {type(e).__name__}: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error("Login failed")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentActiveUser):
    """Get current authenticated user's profile. Requires valid JWT token."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: CurrentActiveUser):
    """
    Logout endpoint (stateless - discard token on client side).
    Can be extended to implement token blacklisting.
    """
    return {"message": "Successfully logged out"}
