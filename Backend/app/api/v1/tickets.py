from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from pydantic import BaseModel

from app.services.project_service import ProjectService
from app.dependencies.auth import CurrentActiveUser
from app.dependencies.tickets import TicketServiceDep
from app.db.session import SessionDep
from app.schemas.ticket import TicketCreate, TicketWithDetails, TicketUpdate, Status
from app.models.ticket import Ticket, IssueType, Priority
from app.models.project import Project
from app.models.user import User

# Request schemas
class AssignTicketRequest(BaseModel):
    assignee_username: str

class ChangeStatusRequest(BaseModel):
    status: Status
    resolution: str = None

class ProjectMemberResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str

class SearchResponse(BaseModel):
    """Response for search/filter operations"""
    total: int
    count: int
    items: List[TicketWithDetails]
    skip: int
    limit: int

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketWithDetails, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    try:
        project_service = ProjectService(db)
        
        # Get project by name to check membership
        result = await db.execute(
            select(Project).where(Project.name == ticket_data.project_name)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project '{ticket_data.project_name}' not found")
        
        # Verify user is member of the project
        is_member = await project_service.is_member(
            project.id, 
            current_user.id
        )
        if not is_member:
            raise PermissionError("You are not a member of this project")
        
        # Create ticket
        ticket = await service.create_ticket(
            data=ticket_data.model_dump(),
            created_by=current_user.id
        )
        return TicketWithDetails.model_validate(ticket)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{project_name}", response_model=List[TicketWithDetails])
async def list_tickets(
    project_name: str,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    try:
        project_service = ProjectService(db)
        
        # Get project by name
        result = await db.execute(
            select(Project).where(Project.name == project_name)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        # Verify user is member of the project
        is_member = await project_service.is_member(
            project.id, 
            current_user.id
        )
        if not is_member:
            raise PermissionError("You are not a member of this project")
        
        # Get tickets
        tickets = await service.get_tickets(project_id=project.id)
        return [TicketWithDetails.model_validate(t) for t in tickets]
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ========== ENDPOINT 1: GET SINGLE TICKET ==========
@router.get("/{ticket_id}", response_model=TicketWithDetails)
async def get_ticket(
    ticket_id: UUID,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Get a single ticket by ID"""
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Check permission - user must be in the project
        project_service = ProjectService(db)
        is_member = await project_service.is_member(ticket.project_id, current_user.id)
        if not is_member:
            raise PermissionError("You don't have access to this ticket")
        
        return TicketWithDetails.model_validate(ticket)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ========== ENDPOINT 2: UPDATE TICKET DETAILS ==========
@router.patch("/{ticket_id}", response_model=TicketWithDetails)
async def update_ticket(
    ticket_id: UUID,
    update_data: TicketUpdate,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Update ticket details (title, description, priority, etc.)"""
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Only reporter or assignee can update
        if ticket.reporter_id != current_user.id and ticket.assignee_id != current_user.id:
            raise PermissionError("Only reporter or assignee can update this ticket")
        
        updated_ticket = await service.update_ticket(ticket_id, update_data.model_dump(exclude_unset=True))
        return TicketWithDetails.model_validate(updated_ticket)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ========== ENDPOINT 3: CHANGE TICKET STATUS ==========
@router.patch("/{ticket_id}/status", response_model=TicketWithDetails)
async def change_ticket_status(
    ticket_id: UUID,
    status_data: ChangeStatusRequest,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Change ticket status (todo → in_progress → done, etc.)"""
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Only assignee or reporter can change status
        if ticket.assignee_id != current_user.id and ticket.reporter_id != current_user.id:
            raise PermissionError("Only assignee or reporter can change status")
        
        updated_ticket = await service.update_ticket_status(
            ticket_id, 
            status_data.status,
            status_data.resolution
        )
        return TicketWithDetails.model_validate(updated_ticket)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ========== ENDPOINT 4: ASSIGN TICKET TO DEVELOPER ==========
@router.patch("/{ticket_id}/assign", response_model=TicketWithDetails)
async def assign_ticket(
    ticket_id: UUID,
    assign_data: AssignTicketRequest,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Assign ticket to a developer (by username)"""
    try:
        ticket = await service.get_ticket_by_id(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Get project to check permissions
        project_service = ProjectService(db)
        is_member = await project_service.is_member(ticket.project_id, current_user.id)
        if not is_member:
            raise PermissionError("You don't have access to this project")
        
        # Find user by username
        result = await db.execute(
            select(User).where(User.username == assign_data.assignee_username)
        )
        assignee = result.scalar_one_or_none()
        if not assignee:
            raise ValueError(f"User '{assign_data.assignee_username}' not found")
        
        # Verify assignee is in the project
        is_assignee_member = await project_service.is_member(ticket.project_id, assignee.id)
        if not is_assignee_member:
            raise ValueError(f"User '{assign_data.assignee_username}' is not a member of this project")
        
        updated_ticket = await service.assign_ticket(ticket_id, assignee.id)
        return TicketWithDetails.model_validate(updated_ticket)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ========== ENDPOINT 5: GET PROJECT MEMBERS ==========
@router.get("/project/{project_id}/members", response_model=List[ProjectMemberResponse])
async def get_project_members(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Get list of members in a project (for assignment dropdown)"""
    try:
        project_service = ProjectService(db)
        
        # Check if user is member of project
        is_member = await project_service.is_member(project_id, current_user.id)
        if not is_member:
            raise PermissionError("You don't have access to this project")
        
        # Get all members of the project (ProjectMember objects)
        project_members = await project_service.get_project_members(project_id)
        
        # Convert to response format with user details
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
        
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== ENDPOINT 6: SEARCH & FILTER TICKETS ==========
@router.get("/{project_name}/search", response_model=SearchResponse)
async def search_tickets(
    project_name: str,
    service: TicketServiceDep,
    db: SessionDep,
    current_user: CurrentActiveUser,
    # Search parameters
    keyword: Optional[str] = Query(None, min_length=1, description="Search in title, description, and ticket key"),
    status: Optional[Status] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    issue_type: Optional[IssueType] = Query(None, description="Filter by issue type"),
    assignee_id: Optional[UUID] = Query(None, description="Filter by assignee ID"),
    reporter_id: Optional[UUID] = Query(None, description="Filter by reporter ID"),
    # Pagination and sorting
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    sort_by: str = Query("created_at", description="Field to sort by: created_at, updated_at, priority, status, title"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order: asc or desc")
):
    """
    Advanced search and filter for tickets with multiple options.
    
    Query Parameters:
    - keyword: Search in title, description, and ticket key (case-insensitive)
    - status: Filter by ticket status (idea, todo, in_progress, in_review, done, cancelled)
    - priority: Filter by priority (low, medium, high, critical)
    - issue_type: Filter by type (bug, feature, task)
    - assignee_id: Filter by assignee UUID
    - reporter_id: Filter by reporter UUID
    - sort_by: created_at, updated_at, priority, status, title
    - sort_order: asc or desc
    - skip: Pagination offset
    - limit: Number of results (max 100)
    """
    try:
        project_service = ProjectService(db)
        
        # Get project by name
        result = await db.execute(
            select(Project).where(Project.name == project_name)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project '{project_name}' not found"
            )
        
        # Verify user is member of the project
        is_member = await project_service.is_member(project.id, current_user.id)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this project"
            )
        
        # Perform search
        tickets, total_count = await service.search_tickets(
            project_id=project.id,
            keyword=keyword,
            status=status,
            priority=priority,
            issue_type=issue_type,
            assignee_id=assignee_id,
            reporter_id=reporter_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return SearchResponse(
            total=total_count,
            count=len(tickets),
            items=[TicketWithDetails.model_validate(t) for t in tickets],
            skip=skip,
            limit=limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )