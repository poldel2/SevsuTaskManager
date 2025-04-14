from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from models.schemas.projects import Project


# from models.schemas.tasks import TaskResponse


class SprintBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(None)


class SprintCreate(SprintBase):
    pass

class SprintUpdate(SprintBase):
    pass


class SprintResponse(SprintBase):
    id: int
    project_id: int

    model_config = {"from_attributes": True}