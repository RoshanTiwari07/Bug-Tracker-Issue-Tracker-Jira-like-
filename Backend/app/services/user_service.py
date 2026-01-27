from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.access_token import get_password_hash, verify_password
from app.services.base import BaseService


class UserService(BaseService):
    """User service for business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return await self._get(user_id)
    
    async def create_user(self, user: UserCreate) -> User:
        """Create new user"""
        # Check if email exists
        existing = await self.get_user_by_email(user.email)
        if existing:
            raise ValueError(f"Email '{user.email}' already registered")
        
        # Check if username exists
        existing = await self.get_user_by_username(user.username)
        if existing:
            raise ValueError(f"Username '{user.username}' already taken")
        
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            timezone=user.timezone
        )
        return await self._add(db_user)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def get_all_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        """Get all users with pagination"""
        query = select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_user(self, user_id: UUID, update_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await self._get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        
        # Check if new email is already taken
        if update_data.email and update_data.email != user.email:
            existing = await self.get_user_by_email(update_data.email)
            if existing:
                raise ValueError(f"Email '{update_data.email}' already in use")
        
        # Check if new username is already taken
        if update_data.username and update_data.username != user.username:
            existing = await self.get_user_by_username(update_data.username)
            if existing:
                raise ValueError(f"Username '{update_data.username}' already taken")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(user, field, value)
        
        return await self._update(user)
    
    async def toggle_user_active(self, user_id: UUID, is_active: bool) -> Optional[User]:
        """Toggle user active status (admin only)"""
        user = await self._get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        
        user.is_active = is_active
        return await self._update(user)
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user (admin only)"""
        user = await self._get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        
        await self._delete(user)
        return True
    
    async def count_users(self) -> int:
        """Count total users in system"""
        query = select(User)
        result = await self.session.execute(query)
        return len(result.scalars().all())
