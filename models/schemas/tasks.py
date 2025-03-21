from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field("todo")  # to do, in_progress, done
    priority: Optional[str] = Field("medium", max_length=10)  # low, medium, high
    column_id: Optional[int] = None

class TaskCreate(TaskBase):
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None

class TaskUpdate(TaskBase):
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project_id: int
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    column_name: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj):
        data = obj.__dict__.copy()
        data["assignee_name"] = obj.assignee.last_name if obj.assignee else None
        data["column_name"] = obj.column.name if obj.column else None  # Добавляем имя столбца
        return cls(**data)
