"""
Tickets API Router - Clean, production-level endpoints
All business logic is delegated to services and permission checking to utilities.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy import select

from app.schemas.ticket import TicketCreate, TicketWithDetails, TicketUpdate, Status
from app.models.ticket import IssueType, Priority
from app.models.user import User
from app.dependencies.auth import CurrentActiveUser
from app.dependencies.tickets import TicketServiceDep
from app.db.session import SessionDep
from app.services.project_service import ProjectService
from app.utils.router_helpers import PermissionChecker, ResponseBuilder
from app.schemas.user import UserResponse
from pydantic import BaseModel
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

# ============= REQUEST SCHEMAS =============
class AssignTicketRequest(BaseModel):
    """Assign ticket to a developer by username"""
    assignee_username: str

class ChangeStatusRequest(BaseModel):
    """Change ticket status with optional resolution"""
    status: Status
    resolution: Optional[str] = None

class ProjectMemberResponse(BaseModel):
    """Response model for project members"""
    id: UUID
    username: str
    email: str
    full_name: str

class SearchResponse(BaseModel):
    """Paginated search results"""
    total: int
    count: int
    items: List[TicketWithDetails]
    skip: int
    limit: int


# ============= ROUTER SETUP =============
router = APIRouter(prefix="/tickets", tags=["tickets"])


# ============= DEPENDENCY INJECTIONS =============
async def get_permission_checker(db: SessionDep) -> PermissionChecker:
    """Inject permission checker utility"""
    return PermissionChecker(db)


# ============= ENDPOINTS =============

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    Create a new ticket in a project.
    User must be a member of the project.
    """
    try:
        # Get project and verify access
        project = await permission_checker.get_project_by_name(ticket_data.project_name)
        await permission_checker.check_project_access(project.id, current_user.id)
        
        # Create ticket via service
        ticket = await service.create_ticket(
            data=ticket_data.model_dump(),
            created_by=current_user.id
        )
        
        return ResponseBuilder.ticket_response(ticket)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Failed to create ticket: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ticket"
        )


@router.patch("/{ticket_id}", response_model=TicketWithDetails)
async def update_ticket(
    ticket_id: UUID,
    update_data: TicketUpdate,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    Update ticket details (title, description, priority, etc.).
    Available to: developers, reporters, assignees, and project admins.
    """
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Check permission
        await permission_checker.check_ticket_edit_permission(
            ticket,
            current_user.id,
            allow_reporter=True,
            allow_assignee=True
        )
        
        # Update via service
        updated_ticket = await service.update_ticket(
            ticket_id,
            update_data.model_dump(exclude_unset=True)
        )
        return TicketWithDetails.model_validate(updated_ticket)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update ticket: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ticket"
        )


@router.patch("/{ticket_id}/status", response_model=TicketWithDetails)
async def change_ticket_status(
    ticket_id: UUID,
    status_data: ChangeStatusRequest,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    Change ticket status (todo → in_progress → done, etc.).
    Available to: developers, assignees, reporters, and project admins.
    """
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Check permission
        await permission_checker.check_ticket_edit_permission(
            ticket,
            current_user.id,
            allow_reporter=True,
            allow_assignee=True
        )
        
        # Update status via service
        updated_ticket = await service.update_ticket_status(
            ticket_id,
            status_data.status,
            status_data.resolution
        )
        return TicketWithDetails.model_validate(updated_ticket)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update ticket status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ticket status"
        )


@router.patch("/{ticket_id}/assign", response_model=TicketWithDetails)
async def assign_ticket(
    ticket_id: UUID,
    assign_data: AssignTicketRequest,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    Assign ticket to a developer (by username).
    Assignee must be a member of the project.
    """
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        # Check current user has access to project
        await permission_checker.check_project_access(ticket.project_id, current_user.id)
        
        # Get assignee user
        assignee = await permission_checker.get_user_by_username(assign_data.assignee_username)
        
        # Verify assignee is in the project
        project_service = ProjectService(db)
        is_assignee_member = await project_service.is_member(ticket.project_id, assignee.id)
        if not is_assignee_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{assign_data.assignee_username}' is not a member of this project"
            )
        
        # Assign ticket
        updated_ticket = await service.assign_ticket(ticket_id, assignee.id)
        return TicketWithDetails.model_validate(updated_ticket)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to assign ticket: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign ticket"
        )


@router.get("/project/{project_id}/members", response_model=List[ProjectMemberResponse])
async def get_project_members(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    Get list of members in a project (for assignment dropdown).
    User must be a member of the project.
    """
    try:
        # Check access
        await permission_checker.check_project_access(project_id, current_user.id)
        
        # Get members
        project_service = ProjectService(db)
        project_members = await project_service.get_project_members(project_id)
        
        # Build response
        result_members = []
        for pm in project_members:
            user = await db.get(User, pm.user_id)
            if user:
                result_members.append(ProjectMemberResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name or ""
                ))
        
        return result_members
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get project members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project members"
        )


@router.get("/{project_name}/search", response_model=SearchResponse)
async def search_tickets(
    project_name: str,
    db: SessionDep,
    service: TicketServiceDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker),
    # Search parameters
    keyword: Optional[str] = Query(None, min_length=1, description="Search in title, description, and key"),
    ticket_status: Optional[Status] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    issue_type: Optional[IssueType] = Query(None, description="Filter by issue type"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee ID"),
    reporter_id: Optional[UUID] = Query(None, description="Filter by reporter ID"),
    # Pagination
    skip: int = Query(0, ge=0, description="Skip count"),
    limit: int = Query(20, ge=1, le=100, description="Result limit"),
    # Sorting
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order")
):
    """
    Advanced search and filter for tickets with pagination and sorting.
    """
    try:
        project_name = unquote(project_name)
        
        # Get project
        project = await permission_checker.get_project_by_name(project_name)
        
        # Check access
        await permission_checker.check_project_access(project.id, current_user.id)
        
        # Search via service
        tickets, total_count = await service.search_tickets(
            project_id=project.id,
            keyword=keyword,
            status=ticket_status,
            priority=priority,
            issue_type=issue_type,
            assignee_id=assignee_id,
            reporter_id=reporter_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Build detailed responses
        ticket_responses = []
        for t in tickets:
            reporter_result = await db.execute(
                select(User).where(User.id == t.reporter_id)
            )
            reporter = reporter_result.scalar_one_or_none()
            
            assignee = None
            if t.assignee_id:
                assignee_result = await db.execute(
                    select(User).where(User.id == t.assignee_id)
                )
                assignee = assignee_result.scalar_one_or_none()
            
            ticket_data = {
                'id': t.id,
                'key': t.key,
                'project_id': t.project_id,
                'status': t.status,
                'resolution': t.resolution,
                'assignee_id': t.assignee_id,
                'reporter_id': t.reporter_id,
                'order_index': t.order_index,
                'created_at': t.created_at,
                'updated_at': t.updated_at,
                'resolved_at': t.resolved_at,
                'type': t.type,
                'title': t.title,
                'description': t.description,
                'due_date': t.due_date,
                'priority': t.priority,
                'reporter': UserResponse.model_validate(reporter) if reporter else None,
                'assignee': UserResponse.model_validate(assignee) if assignee else None,
                'comments_count': 0,
                'attachments_count': 0,
                'labels': []
            }
            ticket_responses.append(TicketWithDetails(**ticket_data))
        
        return SearchResponse(
            total=total_count,
            count=len(tickets),
            items=ticket_responses,
            skip=skip,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/{project_name}", response_model=List[TicketWithDetails])
async def list_tickets(
    project_name: str,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser,
    permission_checker: PermissionChecker = Depends(get_permission_checker)
):
    """
    List all tickets in a project.
    User must be a member of the project.
    """
    try:
        project_name = unquote(project_name)
        
        # Get project
        project = await permission_checker.get_project_by_name(project_name)
        
        # Check access
        await permission_checker.check_project_access(project.id, current_user.id)
        
        # Get tickets
        tickets = await service.get_tickets(project_id=project.id)
        return [TicketWithDetails.model_validate(t) for t in tickets]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to list tickets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tickets"
        )
