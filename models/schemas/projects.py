from datetime import datetime, timezone
from pydantic import BaseModel, Field

from models.schemas.users import UserResponse


class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    owner_id: int

    model_config = {"from_attributes": True}