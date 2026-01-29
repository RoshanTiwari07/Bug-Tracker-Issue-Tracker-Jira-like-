from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy import select

from app.db.session import SessionDep
from app.dependencies.auth import CurrentActiveUser
from app.models.invitation import ProjectInvitation, InvitationStatus
from app.models.project import ProjectMember

router = APIRouter(prefix="/me", tags=["Current User"])


@router.get("/invitations")
async def get_user_invitations(db: SessionDep, current_user: CurrentActiveUser):
    """
    Get all pending invitations for the current user.
    """
    try:
        # Query pending invitations for the current user
        stmt = select(ProjectInvitation).where(
            ProjectInvitation.user_id == current_user.id,
            ProjectInvitation.status == InvitationStatus.PENDING.value
        )
        result = await db.execute(stmt)
        invitations = result.scalars().all()
        
        # Format response with project details
        invitation_list = []
        for inv in invitations:
            # Get project name
            from app.models.project import Project
            project = await db.get(Project, inv.project_id)
            
            # Get inviter details
            from app.models.user import User
            inviter = await db.get(User, inv.invited_by)
            
            invitation_list.append({
                "id": str(inv.id),
                "project_id": str(inv.project_id),
                "project_name": project.name if project else "Unknown",
                "role": inv.role,
                "status": inv.status,
                "invited_by": inviter.username if inviter else "Unknown",
                "created_at": inv.created_at.isoformat(),
                "expires_at": inv.expires_at.isoformat(),
            })
        
        return invitation_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invitations: {str(e)}"
        )


@router.post("/invitations/{invitation_id}/accept")
async def accept_invitation(
    invitation_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Accept an invitation to a project. Only the invited user can accept.
    """
    try:
        # Get the invitation
        invitation = await db.get(ProjectInvitation, invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Verify it's for the current user (SECURITY CHECK)
        if invitation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot accept an invitation meant for another user"
            )
        
        # Check if already processed
        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is already {invitation.status}"
            )
        
        # Check if invitation has expired
        if invitation.is_expired():
            invitation.status = InvitationStatus.EXPIRED.value
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This invitation has expired"
            )
        
        # Add user to project as a member with the invited role
        new_member = ProjectMember(
            project_id=invitation.project_id,
            user_id=current_user.id,
            role=invitation.role,
            added_by=invitation.invited_by
        )
        db.add(new_member)
        
        # Update invitation status
        invitation.status = InvitationStatus.ACCEPTED.value
        db.add(invitation)
        
        await db.commit()
        
        return {
            "message": "Invitation accepted successfully",
            "invitation_id": str(invitation_id),
            "project_id": str(invitation.project_id),
            "role": invitation.role
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to accept invitation: {str(e)}"
        )


@router.post("/invitations/{invitation_id}/decline")
async def decline_invitation(
    invitation_id: UUID,
    db: SessionDep,
    current_user: CurrentActiveUser
):
    """
    Decline an invitation to a project. Only the invited user can decline.
    """
    try:
        # Get the invitation
        invitation = await db.get(ProjectInvitation, invitation_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found"
            )
        
        # Verify it's for the current user (SECURITY CHECK)
        if invitation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot decline an invitation meant for another user"
            )
        
        # Check if already processed
        if invitation.status != InvitationStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invitation is already {invitation.status}"
            )
        
        # Update invitation status to declined
        invitation.status = InvitationStatus.DECLINED.value
        db.add(invitation)
        await db.commit()
        
        return {
            "message": "Invitation declined successfully",
            "invitation_id": str(invitation_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decline invitation: {str(e)}"
        )
    return {
        "message": "Invitation declined",
        "invitation_id": invitation_id
    }
