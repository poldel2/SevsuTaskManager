from pydantic import BaseModel

class TaskColumnBase(BaseModel):
    name: str
    position: int = 0
    color: str = "#808080"

class TaskColumnCreate(TaskColumnBase):
    pass

class TaskColumnUpdate(TaskColumnBase):
    name: str | None = None
    position: int | None = None
    color: str | None = None

class TaskColumn(TaskColumnBase):
    id: int
    project_id: int

    model_config = {"from_attributes": True}