from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy import select
from datetime import datetime

from app.db.session import SessionDep
from app.dependencies.auth import CurrentActiveUser
from app.models.invitation import ProjectInvitation, InvitationStatus
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.schemas.project import ProjectResponse
from pydantic import BaseModel

router = APIRouter(prefix="/me/invitations", tags=["Invitations"])


class ProjectInvitationResponse(BaseModel):
    id: str
    project: ProjectResponse
    role: str
    invited_by: dict
    created_at: str
    expires_at: str
    status: str

    class Config:
        from_attributes = True


class InvitationCreate(BaseModel):
    user_id: UUID
    role: str


@router.get("", response_model=List[ProjectInvitationResponse])
async def get_user_invitations(
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Get all pending invitations for the current user"""
    try:
        # Get all pending invitations for the user
        result = await db.execute(
            select(ProjectInvitation).where(
                ProjectInvitation.user_id == current_user.id,
                ProjectInvitation.status == InvitationStatus.PENDING.value
            )
        )
        invitations = result.scalars().all()
        
        # Build response with full project and user details
        response_data = []
        for inv in invitations:
            invited_by_user = await db.get(User, inv.invited_by)
            response_data.append({
                "id": str(inv.id),
                "project": ProjectResponse.model_validate(inv.project),
                "role": inv.role,
                "invited_by": {
                    "id": str(invited_by_user.id),
                    "username": invited_by_user.username,
                    "full_name": invited_by_user.full_name,
                    "avatar_url": invited_by_user.avatar_url,
                } if invited_by_user else {},
                "created_at": inv.created_at.isoformat() if inv.created_at else None,
                "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
                "status": inv.status,
            })
        
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invitations: {str(e)}"
        )


@router.post("/{invitation_id}/accept", status_code=status.HTTP_200_OK)
async def accept_invitation(
    invitation_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Accept a project invitation"""
    try:
        # Get the invitation
        invitation = await db.get(ProjectInvitation, invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Verify it's for the current user
        if invitation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot accept this invitation"
            )
        
        # Check if already processed
        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is already {invitation.status}"
            )
        
        # Add user to project as a member with the invited role
        new_member = ProjectMember(
            project_id=invitation.project_id,
            user_id=current_user.id,
            role=invitation.role
        )
        db.add(new_member)
        
        # Update invitation status
        invitation.status = InvitationStatus.ACCEPTED.value
        db.add(invitation)
        
        await db.commit()
        
        return {"message": "Invitation accepted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept invitation: {str(e)}"
        )


@router.post("/{invitation_id}/decline", status_code=status.HTTP_200_OK)
async def decline_invitation(
    invitation_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """Decline a project invitation"""
    try:
        # Get the invitation
        invitation = await db.get(ProjectInvitation, invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Verify it's for the current user
        if invitation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot decline this invitation"
            )
        
        # Check if already processed
        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is already {invitation.status}"
            )
        
        # Update invitation status
        invitation.status = InvitationStatus.DECLINED.value
        db.add(invitation)
        
        await db.commit()
        
        return {"message": "Invitation declined successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decline invitation: {str(e)}"
        )
