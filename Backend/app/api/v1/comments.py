"""
Comments API - Clean, production-level comment management
All validation and permission checking delegated to services.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
import logging

from app.dependencies.auth import CurrentActiveUser, SessionDep
from app.dependencies.comments import CommentServiceDep
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate, CommentWithAuthor
from app.models.comment import Comment
from app.models.user import User
from app.models.ticket import Ticket
from app.services.project_service import ProjectService
from app.utils.router_helpers import ErrorHandler

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["comments"])

# ============= HELPERS =============

async def _verify_ticket_exists(ticket_id: UUID, db: SessionDep) -> Ticket:
    """Helper to verify ticket exists, raises 404 if not"""
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise ErrorHandler.handle_not_found("Ticket")
    return ticket


async def _verify_comment_ownership_or_admin(
    comment: Comment,
    user_id: UUID,
    is_admin: bool
) -> bool:
    """Helper to verify comment ownership"""
    if comment.author_id != user_id and not is_admin:
        raise ErrorHandler.handle_permission_denied("You can only modify your own comments")
    return True


# ============= ENDPOINTS =============

@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    ticket_id: UUID,
    comment_data: CommentCreate,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Create a new comment on a ticket (developers and admins only)"""
    try:
        # Verify ticket and user permissions
        await _verify_ticket_exists(ticket_id, db)
        
        # Create comment (service handles all validation)
        comment = await service.create_comment(
            ticket_id=ticket_id,
            author_id=current_user.id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
            user_role_hint=current_user.role  # For permission checks
        )
        
        return CommentResponse.model_validate(comment)
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create comment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/{ticket_id}/comments", response_model=List[CommentWithAuthor])
async def list_ticket_comments(
    ticket_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep,
    skip: int = 0,
    limit: int = 20
):
    """Get all top-level comments for a ticket"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        comments = await service.get_ticket_comments(
            ticket_id=ticket_id,
            skip=skip,
            limit=limit,
            parent_id=None  # Top-level only
        )
        
        # Enrich with author details
        enriched = []
        for comment in comments:
            author = await db.get(User, comment.author_id)
            replies = await service.get_comment_replies(comment.id)
            
            enriched.append(CommentWithAuthor(
                **comment.__dict__,
                author=author,
                replies=replies
            ))
        
        return enriched
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list comments: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/{ticket_id}/comments/{comment_id}", response_model=CommentWithAuthor)
async def get_comment(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Get a specific comment with author and replies"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        comment = await service.get_comment_by_id(comment_id)
        if not comment or comment.ticket_id != ticket_id:
            raise ErrorHandler.handle_not_found("Comment")
        
        author = await db.get(User, comment.author_id)
        replies = await service.get_comment_replies(comment_id)
        
        return CommentWithAuthor(
            **comment.__dict__,
            author=author,
            replies=replies
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get comment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.put("/{ticket_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    ticket_id: UUID,
    comment_id: UUID,
    comment_data: CommentUpdate,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Update a comment (author only)"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        comment = await service.get_comment_by_id(comment_id)
        if not comment or comment.ticket_id != ticket_id:
            raise ErrorHandler.handle_not_found("Comment")
        
        await _verify_comment_ownership_or_admin(comment, current_user.id, is_admin=False)
        
        updated = await service.update_comment(
            comment_id=comment_id,
            author_id=current_user.id,
            content=comment_data.content
        )
        
        return CommentResponse.model_validate(updated)
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update comment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.delete("/{ticket_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Delete a comment (author only)"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        comment = await service.get_comment_by_id(comment_id)
        if not comment or comment.ticket_id != ticket_id:
            raise ErrorHandler.handle_not_found("Comment")
        
        await _verify_comment_ownership_or_admin(comment, current_user.id, is_admin=False)
        
        await service.delete_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=False
        )
    except ValueError as e:
        raise ErrorHandler.handle_validation_error(str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete comment: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()


@router.get("/{ticket_id}/comments/{comment_id}/replies", response_model=List[CommentResponse])
async def get_comment_replies(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep,
    skip: int = 0,
    limit: int = 20
):
    """Get all replies to a comment"""
    try:
        await _verify_ticket_exists(ticket_id, db)
        
        parent = await service.get_comment_by_id(comment_id)
        if not parent or parent.ticket_id != ticket_id:
            raise ErrorHandler.handle_not_found("Comment")
        
        replies = await service.get_comment_replies(
            parent_id=comment_id,
            skip=skip,
            limit=limit
        )
        
        return [CommentResponse.model_validate(r) for r in replies]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get replies: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error()



@router.get("/{ticket_id}/comments", response_model=List[CommentWithAuthor])
async def list_ticket_comments(
    ticket_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep,
    skip: int = 0,
    limit: int = 20
):
    """Get all top-level comments for a ticket"""
    try:
        # Verify ticket exists
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Get comments
        comments = await service.get_ticket_comments(
            ticket_id=ticket_id,
            skip=skip,
            limit=limit,
            parent_id=None  # Only top-level comments
        )
        
        # Enrich with author details
        enriched_comments = []
        for comment in comments:
            author = await db.get(User, comment.author_id)
            replies = await service.get_comment_replies(comment.id)
            
            enriched_comment = CommentWithAuthor(
                **comment.__dict__,
                author=author,
                replies=replies
            )
            enriched_comments.append(enriched_comment)
        
        return enriched_comments
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{ticket_id}/comments/{comment_id}", response_model=CommentWithAuthor)
async def get_comment(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Get a specific comment with author details"""
    try:
        # Verify ticket exists
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Get comment
        comment = await service.get_comment_by_id(comment_id)
        if not comment or comment.ticket_id != ticket_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Get author and replies
        author = await db.get(User, comment.author_id)
        replies = await service.get_comment_replies(comment_id)
        
        return CommentWithAuthor(
            **comment.__dict__,
            author=author,
            replies=replies
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{ticket_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    ticket_id: UUID,
    comment_id: UUID,
    comment_data: CommentUpdate,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Update a comment (only by the author)"""
    try:
        # Verify ticket exists
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Get comment
        comment = await service.get_comment_by_id(comment_id)
        if not comment or comment.ticket_id != ticket_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Verify author
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own comments"
            )
        
        # Update comment
        updated_comment = await service.update_comment(
            comment_id=comment_id,
            author_id=current_user.id,
            content=comment_data.content
        )
        
        return CommentResponse.model_validate(updated_comment)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/{ticket_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep
):
    """Delete a comment (only by the author)"""
    try:
        # Verify ticket exists
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Get comment
        comment = await service.get_comment_by_id(comment_id)
        if not comment or comment.ticket_id != ticket_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Delete comment
        await service.delete_comment(
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=False
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/{ticket_id}/comments/{comment_id}/replies", response_model=List[CommentResponse])
async def get_comment_replies(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: CurrentActiveUser,
    service: CommentServiceDep,
    db: SessionDep,
    skip: int = 0,
    limit: int = 20
):
    """Get all replies to a specific comment"""
    try:
        # Verify ticket exists
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Verify parent comment exists and belongs to ticket
        parent = await service.get_comment_by_id(comment_id)
        if not parent or parent.ticket_id != ticket_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Get replies
        replies = await service.get_comment_replies(
            parent_id=comment_id,
            skip=skip,
            limit=limit
        )
        
        return [CommentResponse.model_validate(r) for r in replies]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
