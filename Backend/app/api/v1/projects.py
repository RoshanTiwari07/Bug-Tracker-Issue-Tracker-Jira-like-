from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import select

from app.db.session import SessionDep
from app.dependencies.auth import CurrentActiveUser
from app.services.project_service import ProjectService
from app.models.ticket import Ticket
from app.schemas.project import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse,
    ProjectMemberAdd,
    ProjectMemberUpdate,
    ProjectMemberResponse
)


class MemberRoleUpdate(BaseModel):
    role: str


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: SessionDep,
    current_user: CurrentActiveUser  # Anyone can create projects
):
    """
    Create a new project. Creator becomes project owner.
    
    - **name**: Project name
    - **key**: Unique project key (2-10 uppercase letters/numbers, e.g., "BUG")
    - **description**: Optional project description
    - **is_private**: Whether project is private (default: true)
    """
    try:
        service = ProjectService(db)
        project = await service.create_project(
            data=project_data.model_dump(),
            created_by=current_user.id
        )
        return ProjectResponse.model_validate(project)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    List all projects where user is a member.
    """
    service = ProjectService(db)
    projects = await service.get_user_projects(current_user.id)
    
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}/me/role")
async def get_current_user_role(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Get the current user's role in a project.
    """
    service = ProjectService(db)
    try:
        role = await service.get_member_role(project_id, current_user.id)
        return {"role": role}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this project"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Get project details by ID"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user is a member
    is_member = await service.is_member(project_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Update project details (Project owner only).
    """
    service = ProjectService(db)
    
    # Check if user is project owner
    member_role = await service.get_member_role(project_id, current_user.id)
    role_value = member_role.value if hasattr(member_role, 'value') else member_role
    if member_role is None or role_value != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can update projects"
        )
    
    try:
        # Only update non-None fields
        update_data = project_data.model_dump(exclude_unset=True)
        project = await service.update_project(project_id, update_data)
        return ProjectResponse.model_validate(project)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Permanently delete a project and all related data (Admin only)"""
    service = ProjectService(db)
    
    # Check if user is project admin
    member_role = await service.get_member_role(project_id, current_user.id)
    role_value = member_role.value if hasattr(member_role, 'value') else member_role
    if member_role is None or role_value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project admins can delete projects"
        )
    
    try:
        await service.delete_project(project_id)
        return {"message": "Project deleted successfully", "project_id": str(project_id)}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Project Members Management
@router.post("/{project_id}/members", response_model=ProjectMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: UUID,
    member_data: ProjectMemberAdd,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Add a member to the project (Project owner/admin only).
    """
    service = ProjectService(db)
    
    # Check if user is project owner or admin
    member_role = await service.get_member_role(project_id, current_user.id)
    role_value = member_role.value if hasattr(member_role, 'value') else member_role
    if member_role is None or role_value not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners/admins can add members"
        )
    
    try:
        member = await service.add_member(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
            added_by=current_user.id
        )
        return ProjectMemberResponse.model_validate(member)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """List all members of a project"""
    service = ProjectService(db)
    
    # Check if user is a member
    is_member = await service.is_member(project_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    members = await service.get_project_members(project_id)
    return [ProjectMemberResponse.model_validate(m) for m in members]


@router.get("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def get_project_member(
    project_id: UUID,
    user_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Get a specific member of a project"""
    service = ProjectService(db)
    
    # Check if user is a member
    is_member = await service.is_member(project_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get the member
    members = await service.get_project_members(project_id)
    member = next((m for m in members if m.user_id == user_id), None)
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found in this project"
        )
    
    return ProjectMemberResponse.model_validate(member)


@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    role_data: ProjectMemberUpdate,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Update a member's role in the project (Project owner only).
    """
    service = ProjectService(db)
    
    # Check if user is project owner
    member_role = await service.get_member_role(project_id, current_user.id)
    role_value = member_role.value if hasattr(member_role, 'value') else member_role
    if member_role is None or role_value != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can update member roles"
        )
    
    try:
        member = await service.update_member_role(
            project_id=project_id,
            user_id=user_id,
            role=role_data.role
        )
        return ProjectMemberResponse.model_validate(member)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )




@router.put("/{project_id}/members/{member_id}")
async def update_project_member_role(
    project_id: UUID,
    member_id: str,
    update_data: MemberRoleUpdate,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Update a member's role in the project (Project owner only).
    Accepts member_id as UUID or username.
    """
    from sqlalchemy import select
    from app.models.user import User
    from sqlalchemy.exc import SQLAlchemyError
    
    service = ProjectService(db)
    
    # Check if user is project owner
    member_role = await service.get_member_role(project_id, current_user.id)
    role_value = member_role.value if hasattr(member_role, 'value') else member_role
    if member_role is None or role_value != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can change member roles"
        )
    
    # Try to parse as UUID, otherwise treat as username
    user_id = None
    try:
        user_id = UUID(member_id)
    except ValueError:
        # It's likely a username, look it up
        try:
            result = await db.execute(
                select(User).where(User.username == member_id)
            )
            user = result.scalar_one_or_none()
            if user:
                user_id = user.id
        except SQLAlchemyError:
            pass
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid member_id or username"
        )
    
    try:
        await service.update_member_role(project_id, user_id, update_data.role)
        return {"message": "Member role updated successfully", "role": update_data.role}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Remove a member from the project (Project owner only).
    """
    service = ProjectService(db)
    
    # Check if user is project owner
    member_role = await service.get_member_role(project_id, current_user.id)
    role_value = member_role.value if hasattr(member_role, 'value') else member_role
    if member_role is None or role_value != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can remove members"
        )
    
    try:
        await service.remove_member(project_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{project_id}/stats")
async def get_project_stats(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Get statistics for a project (ticket counts, members, etc.)
    """
    service = ProjectService(db)
    
    # Check if user is a member
    is_member = await service.is_member(project_id, current_user.id)
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        # Get project details
        project = await service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get all tickets for this project
        tickets_query = select(Ticket).where(Ticket.project_id == project_id)
        result = await db.execute(tickets_query)
        tickets = result.scalars().all()
        
        # Get member count
        members = await service.get_project_members(project_id)
        member_count = len(members) if members else 0
        
        # Calculate stats
        total_tickets = len(tickets)
        
        # Count by status
        tickets_by_status = {}
        for ticket in tickets:
            status_str = str(ticket.status)
            tickets_by_status[status_str] = tickets_by_status.get(status_str, 0) + 1
        
        # Count by priority
        tickets_by_priority = {}
        for ticket in tickets:
            priority_str = str(ticket.priority)
            tickets_by_priority[priority_str] = tickets_by_priority.get(priority_str, 0) + 1
        
        # Count overdue tickets (tickets with status not "done" and past due date)
        overdue_count = 0
        from datetime import datetime
        now = datetime.utcnow()
        for ticket in tickets:
            if ticket.due_date and ticket.due_date < now and str(ticket.status) != "done":
                overdue_count += 1
        
        # Calculate completion rate
        completed = tickets_by_status.get("done", 0)
        completion_rate = int((completed / total_tickets * 100) if total_tickets > 0 else 0)
        
        # Return stats
        return {
            "total_tickets": total_tickets,
            "tickets_by_status": tickets_by_status,
            "tickets_by_priority": tickets_by_priority,
            "overdue_tickets": overdue_count,
            "team_members": member_count,
            "completion_rate": completion_rate
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== SEND PROJECT INVITATION ==========
class InvitationRequest(BaseModel):
    user_id: UUID
    role: str = "developer"


@router.post("/{project_id}/invitations", status_code=status.HTTP_201_CREATED)
async def send_project_invitation(
    project_id: UUID,
    invitation_data: InvitationRequest,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Send an invitation to a user to join the project"""
    from app.models.invitation import ProjectInvitation
    from app.models.user import User
    from app.models.project import Project
    from app.utils.router_helpers import ErrorHandler
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Verify project exists
        project = await db.get(Project, project_id)
        if not project:
            raise ErrorHandler.handle_not_found("Project", project_id)
        
        # Check if user is admin of the project
        service = ProjectService(db)
        user_role = await service.get_member_role(project_id, current_user.id)
        role_value = user_role.value if hasattr(user_role, 'value') else user_role
        if user_role is None or role_value != "admin":
            raise ErrorHandler.handle_permission_denied("Only admins can invite members")
        
        # Verify user exists
        invite_user = await db.get(User, invitation_data.user_id)
        if not invite_user:
            raise ErrorHandler.handle_not_found("User", invitation_data.user_id)
        
        # Check if user is already a member
        is_member = await service.is_member(project_id, invitation_data.user_id)
        if is_member:
            raise ErrorHandler.handle_conflict("User is already a member of this project")
        
        # Create invitation
        invitation = ProjectInvitation(
            project_id=project_id,
            user_id=invitation_data.user_id,
            role=invitation_data.role,
            invited_by=current_user.id
        )
        db.add(invitation)
        await db.flush()
        
        logger.info(f"Invitation created: {invitation.id} for user {invitation_data.user_id} to project {project_id}")
        
        return {
            "id": str(invitation.id),
            "project_id": str(invitation.project_id),
            "user_id": str(invitation.user_id),
            "role": invitation.role,
            "status": invitation.status,
            "created_at": invitation.created_at.isoformat(),
            "expires_at": invitation.expires_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to send invitation: {str(e)}", exc_info=True)
        raise ErrorHandler.handle_internal_error("Failed to create invitation")
