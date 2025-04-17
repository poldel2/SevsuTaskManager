from typing import List, Optional, Dict, Any, Protocol
from fastapi import WebSocket
from models.schemas.notifications import (
    NotificationCreate,
    NotificationResponse,
    TaskNotificationMetadata,
    TeamInvitationMetadata,
    SprintNotificationMetadata
)
from models.domain.notifications import NotificationType
from repositories.notification_repository import NotificationRepository
from .notification_manager import NotificationManager

class NotificationObserver(Protocol):
    async def on_task_assigned(self, user_id: int, task_id: int, task_title: str, project_id: int, project_name: str) -> None:
        ...
    
    async def on_task_updated(self, user_id: int, task_id: int, task_title: str, project_id: int, project_name: str) -> None:
        ...
    
    async def on_team_invitation(self, user_id: int, project_id: int, project_name: str, inviter_id: int, inviter_name: str) -> None:
        ...
    
    async def on_sprint_started(self, user_id: int, sprint_id: int, sprint_name: str, project_id: int, project_name: str) -> None:
        ...

class NotificationService(NotificationObserver):
    def __init__(self, repository: NotificationRepository, notification_manager: NotificationManager):
        self.repository = repository
        self.notification_manager = notification_manager

    def _validate_metadata(self, type: NotificationType, metadata: Dict[str, Any]):
        """Валидация метаданных в зависимости от типа уведомления"""
        validators = {
            NotificationType.TASK_ASSIGNED: TaskNotificationMetadata,
            NotificationType.TASK_UPDATED: TaskNotificationMetadata,
            NotificationType.TEAM_INVITATION: TeamInvitationMetadata,
            NotificationType.SPRINT_STARTED: SprintNotificationMetadata,
            NotificationType.SPRINT_ENDED: SprintNotificationMetadata
        }
        
        if validator := validators.get(type):
            validator(**metadata)

    async def create_notification(
        self,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        notification_metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationResponse:
        if notification_metadata:
            self._validate_metadata(type, notification_metadata)

        notification = await self.repository.create(
            NotificationCreate(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                notification_metadata=notification_metadata
            )
        )
        
        notification_response = NotificationResponse.model_validate(notification)
        await self.notification_manager.send_notification(user_id, notification_response)
        return notification_response

    async def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[NotificationResponse]:
        notifications = await self.repository.get_user_notifications(
            user_id, skip, limit, unread_only
        )
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        return await self.repository.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: int) -> bool:
        return await self.repository.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: int, user_id: int) -> bool:
        return await self.repository.delete(notification_id, user_id)

    async def cleanup_old_notifications(self) -> int:
        return await self.repository.cleanup_old_notifications()

    async def on_task_assigned(self, user_id: int, task_id: int, task_title: str, project_id: int, project_name: str) -> None:
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.TASK_ASSIGNED,
            title="Новая задача",
            message=f"Вам назначена задача '{task_title}'",
            notification_metadata={
                "task_id": task_id,
                "task_title": task_title,
                "project_id": project_id,
                "project_name": project_name
            }
        )

    async def on_task_updated(self, user_id: int, task_id: int, task_title: str, project_id: int, project_name: str) -> None:
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.TASK_UPDATED,
            title="Обновление задачи", 
            message=f"Задача '{task_title}' была обновлена",
            notification_metadata={
                "task_id": task_id,
                "task_title": task_title,
                "project_id": project_id,
                "project_name": project_name
            }
        )

    async def on_team_invitation(self, user_id: int, project_id: int, project_name: str, inviter_id: int, inviter_name: str) -> None:
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.TEAM_INVITATION,
            title="Приглашение в команду",
            message=f"Вас пригласили в проект '{project_name}'",
            notification_metadata={
                "project_id": project_id,
                "project_name": project_name,
                "inviter_id": inviter_id,
                "inviter_name": inviter_name
            }
        )

    async def on_sprint_started(self, user_id: int, sprint_id: int, sprint_name: str, project_id: int, project_name: str) -> None:
        await self.create_notification(
            user_id=user_id,
            type=NotificationType.SPRINT_STARTED,
            title="Спринт начался",
            message=f"Начался спринт '{sprint_name}' в проекте '{project_name}'",
            notification_metadata={
                "sprint_id": sprint_id,
                "sprint_name": sprint_name,
                "project_id": project_id,
                "project_name": project_name
            }
        )