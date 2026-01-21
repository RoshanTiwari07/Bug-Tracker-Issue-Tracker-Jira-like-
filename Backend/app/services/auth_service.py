from datetime import datetime, timezone
from fastapi import BackgroundTasks
from sqlalchemy import select, or_
from app.services.base import BaseService
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from email_validator import validate_email, EmailNotValidError

from app.utils.access_token import create_access_token, get_password_hash, verify_password

class AuthService(BaseService):
    def __init__(self, model: User, session: AsyncSession, tasks: BackgroundTasks):
        self.model = model
        self.session = session
        self.tasks = tasks
    
    async def _add_user(self, data: dict) -> tuple:
        # Extract password before unpacking
        password = data.pop('password', None)
        
        # Validate inputs
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        email = data.get('email')
        username = data.get('username')
        
        if not email or not username:
            raise ValueError("Email and username are required")
        
        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValueError("Invalid email format")
        
        # Check if email or username already exists
        result = await self.session.execute(
            select(User).where(
                or_(User.email == email, User.username == username)
            )
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            if existing_user.email == email:
                raise ValueError("Email already exists")
            else:
                raise ValueError("Username already exists")
        
        # Create user with VIEWER role by default
        user = self.model(
            **data,
            role="viewer",  # Always start as viewer
            hashed_password=get_password_hash(password)
        )
        
        user = await self._add(user)
        token = create_access_token(data={
            "id": str(user.id),
            "email": user.email
        })
        return user, token
    
    async def login_user(self, username_or_email: str, password: str) -> tuple:
        # Validate inputs
        if not username_or_email or not password:
            raise ValueError("Username/email and password are required")
        
        # Find user by email OR username
        result = await self.session.execute(
            select(User).where(
                or_(User.email == username_or_email, User.username == username_or_email)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        user = await self._update(user)
        
        token = create_access_token(data={
            "id": str(user.id),
            "email": user.email
        })
        return user, token