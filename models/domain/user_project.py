from sqlalchemy import Column, Integer, String, ForeignKey, Table
from core.db import Base
from enum import Enum as PyEnum
from sqlalchemy import Enum

class Role(PyEnum):
    OWNER = "owner"
    MEMBER = "member"
    ADMIN = "admin"
    TEACHER = "teacher"

user_project_table = Table(
    "user_project",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("project_id", Integer, ForeignKey("projects.id"), nullable=False),
    Column("role", Enum(Role), nullable=False, default=Role.MEMBER),
)