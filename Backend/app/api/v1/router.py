from fastapi import APIRouter
from app.api.v1 import auth, projects, tickets, comments, attachments, users, me, invitations

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(invitations.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(tickets.router)
api_router.include_router(comments.router)
api_router.include_router(attachments.router)
# api_router.include_router(items.router)  # TODO: Create items router
