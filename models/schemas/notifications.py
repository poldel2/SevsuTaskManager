from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from ..domain.notifications import NotificationType

class NotificationBase(BaseModel):
    type: NotificationType
    title: str
    message: str
    notification_metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    read: bool

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# Специфичные схемы метаданных для валидации
class TaskNotificationMetadata(BaseModel):
    task_id: int
    task_title: str
    project_id: int
    project_name: str

class TeamInvitationMetadata(BaseModel):
    project_id: int
    project_name: str
    inviter_id: int
    inviter_name: str

class SprintNotificationMetadata(BaseModel):
    sprint_id: int
    sprint_name: str
    project_id: int
    project_name: str