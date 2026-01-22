from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.tickets import TicketService

SessionDep = Annotated[AsyncSession, Depends(get_db)]

async def get_ticket_service(db: SessionDep) -> TicketService:
    return TicketService(db)

TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]