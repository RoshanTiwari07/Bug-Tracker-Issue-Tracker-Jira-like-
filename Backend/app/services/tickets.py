from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, and_ , func
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.models.ticket import Priority, Status, Ticket
from app.models.project import Project
from datetime import datetime, timezone


class TicketService(BaseService):
    """Ticket service for business logic"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Ticket

    async def create_ticket(self, data: dict, created_by: UUID) -> Ticket:
        """Create a new ticket with auto-generated key"""
        
        # Get project by name (user-friendly)
        project_name = data.pop('project_name', None)  # Remove from data dict
        if not project_name:
            raise ValueError("project_name is required")
        
        result = await self.session.execute(
            select(Project).where(Project.name == project_name)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        # Set project_id from the found project
        project_id = project.id
        project_key = project.key
        
        # Generate ticket key (e.g., "BUG-1", "BUG-2")
        ticket_result = await self.session.execute(
            select(func.count(Ticket.id)).where(
                Ticket.project_id == project_id
            )
        )
        ticket_count = ticket_result.scalar() or 0
        ticket_key = f"{project_key}-{ticket_count + 1}"
        
        # Check if key is unique (safeguard)
        existing = await self.session.execute(
            select(Ticket).where(Ticket.key == ticket_key)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Ticket key {ticket_key} already exists")
        
        # Create ticket with reporter_id set to created_by
        # assignee_id is None by default (assigned later by admin)
        data['key'] = ticket_key
        data['project_id'] = project_id
        data['reporter_id'] = created_by
        # Don't set assignee_id - leave it null for admin to assign
        
        new_ticket = Ticket(**data)
        return await self._add(new_ticket)
    
    async def get_tickets(
        self,
        project_id: UUID,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        assignee_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Ticket]:
        """Get tickets with filtering and pagination"""
        # Base query
        query = select(Ticket).where(
            and_(
                Ticket.project_id == project_id,
                Ticket.is_archived is not True
            )
        )
        
        # Apply filters if provided
        if status:
            query = query.where(Ticket.status == status)
        
        if priority:
            query = query.where(Ticket.priority == priority)
        
        if assignee_id:
            query = query.where(Ticket.assignee_id == assignee_id)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_ticket_by_id(self, ticket_id: UUID) -> Optional[Ticket]:
        """Get a ticket by ID"""
        return await self._get(ticket_id)
    
    async def update_ticket(self, ticket_id: UUID, data: dict) -> Ticket:
        """Update ticket details"""
        ticket = await self._get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        # Update only allowed fields
        allowed_fields = ['title', 'description', 'type', 'priority', 'due_date']
        for key, value in data.items():
            if key in allowed_fields and value is not None:
                setattr(ticket, key, value)
        
        return await self._update(ticket)
    
    async def update_ticket_status(self, ticket_id: UUID, status: Status, resolution: Optional[str] = None) -> Ticket:
        ticket = await self._get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.status = status
        if resolution:
            ticket.resolution = resolution
        
        # Set resolved_at if status is resolved
        if status == Status.DONE:
            ticket.resolved_at = datetime.now(timezone.utc)
        
        return await self._update(ticket)
    
    async def assign_ticket(self, ticket_id: UUID, assignee_id: UUID) -> Ticket:
        """Assign ticket to a user"""
        ticket = await self._get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.assignee_id = assignee_id
        return await self._update(ticket)