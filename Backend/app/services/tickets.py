from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, and_, func, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.models.ticket import Priority, Status, Ticket, IssueType
from app.models.project import Project
from app.models.user import User
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
    
    async def search_tickets(
        self,
        project_id: UUID,
        keyword: Optional[str] = None,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        issue_type: Optional[IssueType] = None,
        assignee_id: Optional[UUID] = None,
        reporter_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[Ticket], int]:
        """Search and filter tickets with comprehensive options"""
        
        # Base query
        query = select(Ticket).where(
            and_(
                Ticket.project_id == project_id,
                Ticket.is_archived is not True
            )
        )
        
        # Keyword search (searches title and description)
        if keyword:
            search_term = f"%{keyword}%"
            query = query.where(
                or_(
                    Ticket.title.ilike(search_term),
                    Ticket.description.ilike(search_term),
                    Ticket.key.ilike(search_term)
                )
            )
        
        # Filter by status
        if status:
            query = query.where(Ticket.status == status)
        
        # Filter by priority
        if priority:
            query = query.where(Ticket.priority == priority)
        
        # Filter by issue type
        if issue_type:
            query = query.where(Ticket.type == issue_type)
        
        # Filter by assignee
        if assignee_id:
            query = query.where(Ticket.assignee_id == assignee_id)
        
        # Filter by reporter
        if reporter_id:
            query = query.where(Ticket.reporter_id == reporter_id)
        
        # Count total results before pagination
        count_query = select(func.count(Ticket.id)).select_from(Ticket).where(
            and_(
                Ticket.project_id == project_id,
                Ticket.is_archived is not True
            )
        )
        if keyword:
            search_term = f"%{keyword}%"
            count_query = count_query.where(
                or_(
                    Ticket.title.ilike(search_term),
                    Ticket.description.ilike(search_term),
                    Ticket.key.ilike(search_term)
                )
            )
        if status:
            count_query = count_query.where(Ticket.status == status)
        if priority:
            count_query = count_query.where(Ticket.priority == priority)
        if issue_type:
            count_query = count_query.where(Ticket.type == issue_type)
        if assignee_id:
            count_query = count_query.where(Ticket.assignee_id == assignee_id)
        if reporter_id:
            count_query = count_query.where(Ticket.reporter_id == reporter_id)
        
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0
        
        # Apply sorting
        sort_column = getattr(Ticket, sort_by, Ticket.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        tickets = result.scalars().all()
        
        # Load related objects for each ticket to avoid lazy loading issues
        for ticket in tickets:
            # Access the relationships to ensure they're loaded
            _ = ticket.reporter_id  # This is already available
            _ = ticket.assignee_id  # This is already available
        
        return tickets, total_count

    
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
        if status == Status.DONE:
            # Set resolution fields when closing
            if resolution:
                ticket.resolution = resolution
            ticket.resolved_at = datetime.now(timezone.utc)
        else:
            # Reopening or moving out of DONE clears resolution metadata
            ticket.resolution = None
            ticket.resolved_at = None
        
        return await self._update(ticket)
    
    async def assign_ticket(self, ticket_id: UUID, assignee_id: UUID) -> Ticket:
        """Assign ticket to a user"""
        ticket = await self._get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        ticket.assignee_id = assignee_id
        return await self._update(ticket)
    
    async def delete_ticket(self, ticket_id: UUID) -> bool:
        """Delete a ticket permanently"""
        ticket = await self._get(ticket_id)
        if not ticket:
            raise ValueError("Ticket not found")
        
        await self.session.delete(ticket)
        return True