from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.schemas.user import UserResponse

class ActionType(str):
    CREATE = "create"
    UPDATE = "update"
    COMMENTED = "commented"
    ASSIGNED = "assigned"
    STATUS_CHANGED = "status_changed"


class ActivityResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    user_id: UUID
    action: ActionType
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    extra_data: Optional[dict] = None
    created_at: datetime

class ActivityWithUser(ActivityResponse):
    user: UserResponse