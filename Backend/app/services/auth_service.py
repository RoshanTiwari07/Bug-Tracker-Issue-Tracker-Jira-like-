from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.core.config import settings
from app.services.user_service import UserService


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def login(db: Session, username: str, password: str) -> dict:
        """Login user and return access token"""
        user = UserService.authenticate_user(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
