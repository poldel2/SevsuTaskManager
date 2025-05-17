from datetime import datetime, timezone
from pydantic import BaseModel, Field

from models.schemas.users import UserResponse


class ProjectBase(BaseModel):
    title: str
    description: str | None = None
    logo: str | None = None
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime | None = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    title: str | None = None
    end_date: datetime | None = None

class Project(ProjectBase):
    id: int
    owner_id: int
    start_date: datetime
    end_date: datetime | None = None

    model_config = {"from_attributes": True}