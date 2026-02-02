"""
Common router utilities and helpers for clean, reusable endpoint logic
"""
from typing import Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.services.project_service import ProjectService


class PermissionChecker:
    """Handle permission checking for ticket and project operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)
    
    async def check_project_access(
        self, 
        project_id: UUID, 
        user_id: UUID,
        require_role: Optional[str] = None
    ) -> bool:
        """
        Check if user has access to project.
        
        Args:
            project_id: Project ID
            user_id: User ID
            require_role: Optional specific role requirement (owner, admin, developer, viewer)
            
        Returns:
            True if has access, raises HTTPException if not
        """
        is_member = await self.project_service.is_member(project_id, user_id)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project"
            )
        
        if require_role:
            user_role = await self.project_service.get_member_role(project_id, user_id)
            if user_role != require_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This action requires {require_role} role"
                )
        
        return True
    
    async def check_ticket_edit_permission(
        self,
        ticket,
        user_id: UUID,
        allow_reporter: bool = True,
        allow_assignee: bool = True
    ) -> bool:
        """
        Check if user can edit a ticket.
        
        Rules:
        - Owner/Admin: can always edit
        - Developer: can edit tickets in their project
        - Reporter: can edit if allow_reporter=True
        - Assignee: can edit if allow_assignee=True
        """
        user_role = await self.project_service.get_member_role(ticket.project_id, user_id)
        
        can_edit = user_role in ["owner", "admin", "developer"]
        
        if not can_edit and allow_reporter and ticket.reporter_id == user_id:
            can_edit = True
        
        if not can_edit and allow_assignee and ticket.assignee_id == user_id:
            can_edit = True
        
        if not can_edit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action"
            )
        
        return True
    
    async def get_user_by_username(self, username: str) -> User:
        """Get user by username, raises HTTPException if not found"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{username}' not found"
            )
        return user
    
    async def get_project_by_name(self, project_name: str) -> Project:
        """Get project by name, raises HTTPException if not found"""
        result = await self.db.execute(
            select(Project).where(Project.name == project_name)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_name}' not found"
            )
        return project
    
    async def get_project_by_id(self, project_id: UUID) -> Project:
        """Get project by ID, raises HTTPException if not found"""
        project = await self.db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project


class ResponseBuilder:
    """Build consistent response objects"""
    
    @staticmethod
    def ticket_response(ticket) -> dict:
        """Convert ticket model to response dict"""
        return {
            "id": str(ticket.id),
            "key": ticket.key,
            "title": ticket.title,
            "description": ticket.description,
            "project_id": str(ticket.project_id),
            "type": ticket.type if isinstance(ticket.type, str) else ticket.type.value,
            "status": ticket.status if isinstance(ticket.status, str) else ticket.status.value,
            "priority": ticket.priority if isinstance(ticket.priority, str) else ticket.priority.value,
            "resolution": ticket.resolution if isinstance(ticket.resolution, str) else (ticket.resolution.value if ticket.resolution else None),
            "assignee_id": str(ticket.assignee_id) if ticket.assignee_id else None,
            "reporter_id": str(ticket.reporter_id),
            "is_archived": ticket.is_archived,
            "order_index": ticket.order_index,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
        }

class ErrorHandler:
    """Centralized error handling for common scenarios"""
    
    @staticmethod
    def handle_not_found(entity_name: str, identifier: str = None) -> HTTPException:
        """Handle resource not found errors"""
        detail = f"{entity_name} not found"
        if identifier:
            detail = f"{entity_name} '{identifier}' not found"
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    @staticmethod
    def handle_validation_error(message: str) -> HTTPException:
        """Handle validation errors"""
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    @staticmethod
    def handle_permission_denied(message: str = None) -> HTTPException:
        """Handle permission denied errors"""
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message or "You don't have permission to perform this action"
        )
    
    @staticmethod
    def handle_conflict(message: str) -> HTTPException:
        """Handle resource conflict errors"""
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )
    
    @staticmethod
    def handle_internal_error(message: str = None) -> HTTPException:
        """Handle internal server errors"""
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message or "An internal server error occurred"
        )