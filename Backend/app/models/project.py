from uuid import uuid4, UUID
from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Enum, Field, SQLModel, Relationship, UniqueConstraint
from datetime import datetime
from app.db.types import project_role_enum

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
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow)
    )
    updated_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow, onupdate=datetime.utcnow)
    )
    members: list["ProjectMember"] = Relationship(back_populates="project")


class ProjectMember(SQLModel, table=True):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="unique_project_user"),
)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(nullable=False, foreign_key="projects.id")
    user_id: UUID = Field(nullable=False, foreign_key="users.id")
    role: ProjectRole = Field(sa_column=Column(project_role_enum), nullable=False)
    joined_at: datetime = Field(
        sa_column=Column(postgresql.TIMESTAMP, default_factory=datetime.utcnow)
    )
    added_by: UUID = Field(nullable=False, foreign_key="users.id")
    user: "User" = Relationship(back_populates="project_memberships", sa_relationship_kwargs={"lazy": "joined"})
    project: "Project" = Relationship(back_populates="members", sa_relationship_kwargs={"lazy": "joined"})
