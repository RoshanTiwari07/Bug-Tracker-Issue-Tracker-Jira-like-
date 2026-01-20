from sqlalchemy.dialects import postgresql

role_enum = postgresql.ENUM(
    "admin", "developer", "viewer",
    name="role_enum",
    create_type=True
)

project_role_enum = postgresql.ENUM(
    "owner", "admin", "developer", "viewer",
    name="project_role_enum",
    create_type=True
)

issue_type_enum = postgresql.ENUM(
    "bug", "feature", "task",
    name="issue_type_enum",
    create_type=True
)

resolution_enum = postgresql.ENUM(
    "fixed", "wont_fix", "duplicate", "incomplete",
    name="resolution_enum",
    create_type=True
)

issuestatus_enum = postgresql.ENUM(
    "in_progress", "cancelled", "done","in_review","todo",
    name="issuestatus_enum",
    create_type=True
)

priority_enum = postgresql.ENUM(
    "low", "medium", "high", "critical",
    name="priority_enum",
    create_type=True 
)