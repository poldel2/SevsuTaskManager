from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional

class TaskBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field("todo")  # to do, in_progress, done
    priority: Optional[str] = Field("medium", max_length=10)  # low, medium, high
    grade: Optional[str] = Field("medium", max_length=10)  # easy, medium, hard
    column_id: Optional[int] = None
    start_date: Optional[datetime] = None

    due_date: datetime | None = None

class TaskCreate(TaskBase):
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)  # to do, in_progress, done
    priority: Optional[str] = Field(None, max_length=10)  # low, medium, high
    grade: Optional[str] = Field(None, max_length=10)  # easy, medium, hard
    column_id: Optional[int] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
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
    feedback: Optional[str] = None
    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj):
        data = obj.__dict__.copy()
        return cls(**data)

class TaskApproval(BaseModel):
    is_teacher_approval: bool = False
    comment: str | None = None

class TaskRejection(BaseModel):
    feedback: str = Field(..., min_length=10)

