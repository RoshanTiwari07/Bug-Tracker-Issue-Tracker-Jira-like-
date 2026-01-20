from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, SQLModel, UniqueConstraint
from datetime import datetime
from app.db.types import project_role_enum
from enum import Enum


class ProjectRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    key: str = Field(max_length=10, unique=True, nullable=False, index=True)
    description: str = Field(nullable=True)
    is_archived: bool = Field(default=False, nullable=False)
    is_private: bool = Field(default=True, nullable=False)
    created_by: UUID = Field(nullable=False, foreign_key="users.id")
    created_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    )


class ProjectMember(SQLModel, table=True):
    model_config = {"arbitrary_types_allowed": True}
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="unique_project_user"),
)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(nullable=False, foreign_key="projects.id")
    user_id: UUID = Field(nullable=False, foreign_key="users.id")
    role: ProjectRole = Field(sa_column=Column(project_role_enum, nullable=False))
    joined_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default=datetime.utcnow)
    )
    added_by: UUID = Field(nullable=False, foreign_key="users.id")
