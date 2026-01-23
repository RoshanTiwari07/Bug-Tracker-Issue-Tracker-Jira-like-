from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.models.comment import Comment
from app.models.ticket import Ticket
from datetime import datetime, timezone


class CommentService(BaseService):
    """Comment service for business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Comment

    async def create_comment(
        self, 
        ticket_id: UUID, 
        author_id: UUID, 
        content: str,
        parent_id: Optional[UUID] = None
    ) -> Comment:
        """Create a new comment on a ticket"""
        
        # Verify ticket exists
        ticket = await self.session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found")
        
        # Create comment
        new_comment = Comment(
            ticket_id=ticket_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id
        )
        return await self._add(new_comment)

    async def get_ticket_comments(
        self,
        ticket_id: UUID,
        skip: int = 0,
        limit: int = 20,
        parent_id: Optional[UUID] = None
    ) -> List[Comment]:
        """Get comments for a ticket (top-level or replies)"""
        
        # Verify ticket exists
        ticket = await self.session.get(Ticket, ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found")
        
        # Base query
        query = select(Comment).where(
            Comment.ticket_id == ticket_id
        )
        
        # Filter by parent_id if provided (for replies)
        if parent_id is not None:
            query = query.where(Comment.parent_id == parent_id)
        else:
            # Get only top-level comments (no parent)
            query = query.where(Comment.parent_id.is_(None))
        
        # Order by creation date
        query = query.order_by(Comment.created_at)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_comment_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Get a comment by ID"""
        return await self._get(comment_id)

    async def update_comment(
        self,
        comment_id: UUID,
        author_id: UUID,
        content: str
    ) -> Optional[Comment]:
        """Update a comment (only by original author)"""
        
        comment = await self._get(comment_id)
        if not comment:
            raise ValueError(f"Comment '{comment_id}' not found")
        
        # Verify author is updating their own comment
        if comment.author_id != author_id:
            raise PermissionError("You can only update your own comments")
        
        # Update comment
        comment.content = content
        comment.is_edited = True
        comment.updated_at = datetime.now(timezone.utc)
        
        return await self._update(comment)

    async def delete_comment(
        self,
        comment_id: UUID,
        user_id: UUID,
        is_admin: bool = False
    ) -> bool:
        """Delete a comment (by author or admin)"""
        
        comment = await self._get(comment_id)
        if not comment:
            raise ValueError(f"Comment '{comment_id}' not found")
        
        # Check permissions
        if comment.author_id != user_id and not is_admin:
            raise PermissionError("You can only delete your own comments")
        
        await self._delete(comment)
        return True

    async def get_comment_replies(
        self,
        parent_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Comment]:
        """Get all replies to a comment"""
        
        # Verify parent comment exists
        parent = await self._get(parent_id)
        if not parent:
            raise ValueError(f"Parent comment '{parent_id}' not found")
        
        query = select(Comment).where(
            Comment.parent_id == parent_id
        ).order_by(Comment.created_at).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_comment_thread(self, parent_id: UUID) -> Optional[dict]:
        """Get a comment with all its replies"""
        
        parent = await self._get(parent_id)
        if not parent:
            raise ValueError(f"Comment '{parent_id}' not found")
        
        # Get all replies
        replies = await self.get_comment_replies(parent_id)
        
        return {
            "comment": parent,
            "replies": replies,
            "reply_count": len(replies)
        }
