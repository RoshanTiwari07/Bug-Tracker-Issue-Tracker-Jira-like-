from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import SessionDep
from app.dependencies.auth import CurrentActiveUser
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, AuthResponse


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
        # Initialize auth service
        auth_service = AuthService(User, db, background_tasks)
        
        # Create user and get token
        user, token = await auth_service._add_user(user_data.model_dump())
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=token,
            token_type="bearer"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the actual error for debugging
        print(f"Registration error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user account: {str(e)}"
        )


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
        # Initialize auth service
        auth_service = AuthService(User, db, background_tasks)
        
        # Authenticate user
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
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Unexpected login error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


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
        # Initialize auth service
        auth_service = AuthService(User, db, background_tasks)
        
        # Authenticate user (username field can be email or username)
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
        print(f"Login form error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        print(f"Unexpected login form error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: CurrentActiveUser):
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: CurrentActiveUser):
    """
    Logout endpoint.
    
    Since JWT is stateless, logout is handled on the client side
    by discarding the token. This endpoint is provided for consistency
    and can be extended to implement token blacklisting if needed.
    """
    return {
        "message": "Successfully logged out",
        "detail": "Please discard your access token on the client side"
    }
