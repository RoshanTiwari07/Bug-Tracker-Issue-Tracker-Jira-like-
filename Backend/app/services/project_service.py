from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base import BaseService
from app.models.project import Project, ProjectMember, ProjectRole
from app.models.user import User


class ProjectService(BaseService):
    """Project service for business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Project
    
    async def create_project(self, data: dict, created_by: UUID) -> Project:
        """Create a new project"""
        # Check if project key already exists
        result = await self.session.execute(
            select(Project).where(Project.key == data.get('key'))
        )
        existing_project = result.scalar_one_or_none()
        if existing_project:
            raise ValueError("Project key already exists")
        
        # Create project
        project = Project(**data, created_by=created_by)
        project = await self._add(project)
        
        # Add creator as OWNER
        member = ProjectMember(
            project_id=project.id,
            user_id=created_by,
            role=ProjectRole.OWNER,
            added_by=created_by
        )
        self.session.add(member)
        
        # Upgrade user's global role to ADMIN if they're still a VIEWER
        user_result = await self.session.execute(
            select(User).where(User.id == created_by)
        )
        user = user_result.scalar_one_or_none()
        if user and user.role == "viewer":
            user.role = "admin"
            self.session.add(user)
        
        await self.session.commit()
        
        return project
    
    async def get_project(self, project_id: UUID) -> Optional[Project]:
        """Get project by ID"""
        return await self._get(project_id)
    
    async def get_user_projects(self, user_id: UUID) -> List[Project]:
        """Get all projects where user is a member"""
        result = await self.session.execute(
            select(Project)
            .join(ProjectMember, Project.id == ProjectMember.project_id)
            .where(ProjectMember.user_id == user_id)
            .where(Project.is_archived == False)
        )
        return result.scalars().all()
    
    async def get_all_projects(self) -> List[Project]:
        """Get all projects (admin only)"""
        result = await self.session.execute(
            select(Project).where(Project.is_archived == False)
        )
        return result.scalars().all()
    
    async def update_project(self, project_id: UUID, data: dict) -> Project:
        """Update project"""
        project = await self._get(project_id)
        if not project:
            raise ValueError("Project not found")
        
        # Check key uniqueness if being updated
        if 'key' in data and data['key'] != project.key:
            result = await self.session.execute(
                select(Project).where(Project.key == data['key'])
            )
            if result.scalar_one_or_none():
                raise ValueError("Project key already exists")
        
        for key, value in data.items():
            if value is not None:
                setattr(project, key, value)
        
        return await self._update(project)
    
    async def delete_project(self, project_id: UUID) -> None:
        """Delete (archive) project"""
        project = await self._get(project_id)
        if not project:
            raise ValueError("Project not found")
        
        project.is_archived = True
        await self._update(project)
    
    async def add_member(
        self, 
        project_id: UUID, 
        user_id: UUID, 
        role: ProjectRole, 
        added_by: UUID
    ) -> ProjectMember:
        """Add member to project"""
        # Check if user exists
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if user's global role is viewer (only viewers can be added to projects)
        if user.role != "viewer":
            raise ValueError("User is already associated with other projects and cannot be added")
        
        # Check if already a member
        result = await self.session.execute(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                )
            )
        )
        if result.scalar_one_or_none():
            raise ValueError("User is already a member of this project")
        
        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
            added_by=added_by
        )
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member
    
    async def get_project_members(self, project_id: UUID) -> List[ProjectMember]:
        """Get all members of a project"""
        result = await self.session.execute(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        return result.scalars().all()
    
    async def update_member_role(
        self, 
        project_id: UUID, 
        user_id: UUID, 
        role: ProjectRole
    ) -> ProjectMember:
        """Update member role in project"""
        result = await self.session.execute(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                )
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise ValueError("Member not found in project")
        
        member.role = role
        await self.session.commit()
        await self.session.refresh(member)
        return member
    
    async def remove_member(self, project_id: UUID, user_id: UUID) -> None:
        """Remove member from project"""
        result = await self.session.execute(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                )
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise ValueError("Member not found in project")
        
        # Don't allow removing the owner
        if member.role == ProjectRole.OWNER:
            raise ValueError("Cannot remove project owner")
        
        await self.session.delete(member)
        await self.session.commit()
    
    async def is_member(self, project_id: UUID, user_id: UUID) -> bool:
        """Check if user is a member of project"""
        result = await self.session.execute(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_member_role(self, project_id: UUID, user_id: UUID) -> Optional[ProjectRole]:
        """Get user's role in project"""
        result = await self.session.execute(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                )
            )
        )
        member = result.scalar_one_or_none()
        return member.role if member else None
