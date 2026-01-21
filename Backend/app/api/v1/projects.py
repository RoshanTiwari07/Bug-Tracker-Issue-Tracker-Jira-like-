from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from app.db.session import SessionDep
from app.dependencies.auth import CurrentActiveUser, AdminUser
from app.services.project_service import ProjectService
from app.schemas.project import (
    ProjectCreate, 
    ProjectUpdate, 
    ProjectResponse,
    ProjectMemberAdd,
    ProjectMemberUpdate,
    ProjectMemberResponse
)

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
    if member_role != "owner":
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


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Archive (soft delete) a project (Project owner only)"""
    service = ProjectService(db)
    
    # Check if user is project owner
    member_role = await service.get_member_role(project_id, current_user.id)
    if member_role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owners can delete projects"
        )
    
    try:
        await service.delete_project(project_id)
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
    if member_role not in ["owner", "admin"]:
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
    if member_role != "owner":
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
    if member_role != "owner":
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
