from typing import List, Optional, Dict, Any
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

class NotificationService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance.websocket_connections = {}  # user_id -> WebSocket
        return cls._instance

    def __init__(self, notification_repository: NotificationRepository):
        if not hasattr(self, 'initialized'):
            self.repository = notification_repository
            self.initialized = True

    async def _send_notification_ws(self, user_id: int, notification: NotificationResponse):
        """Отправка уведомления через WebSocket"""
        if connection := self.websocket_connections.get(user_id):
            try:
                await connection.send_json({
                    "type": "notification",
                    "data": notification.dict()
                })
            except Exception:
                # Если возникла ошибка при отправке, удаляем соединение
                del self.websocket_connections[user_id]

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение нового пользователя"""
        await websocket.accept()
        self.websocket_connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        """Отключение пользователя"""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]

    async def create_notification(
        self,
        user_id: int,
        type: NotificationType,
        title: str,
        message: str,
        notification_metadata: Optional[Dict[str, Any]] = None
    ) -> NotificationResponse:
        # Валидация метаданных в зависимости от типа уведомления
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

        # Отправка уведомления через WebSocket если пользователь онлайн
        await self._send_notification_ws(user_id, NotificationResponse.from_orm(notification))
        
        return NotificationResponse.from_orm(notification)

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
        return [NotificationResponse.from_orm(n) for n in notifications]

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        return await self.repository.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: int) -> bool:
        return await self.repository.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: int, user_id: int) -> bool:
        return await self.repository.delete(notification_id, user_id)

    # Методы для создания специфичных типов уведомлений
    async def notify_task_assigned(
        self,
        user_id: int,
        task_id: int,
        task_title: str,
        project_id: int,
        project_name: str
    ):
        return await self.create_notification(
            user_id=user_id,
            type=NotificationType.TASK_ASSIGNED,
            title=f"Вам назначена задача: {task_title}",
            message=f"Вы назначены исполнителем задачи в проекте {project_name}",
            notification_metadata={
                "task_id": task_id,
                "task_title": task_title,
                "project_id": project_id,
                "project_name": project_name
            }
        )

    async def notify_team_invitation(
        self,
        user_id: int,
        project_id: int,
        project_name: str,
        inviter_id: int,
        inviter_name: str
    ):
        return await self.create_notification(
            user_id=user_id,
            type=NotificationType.TEAM_INVITATION,
            title=f"Приглашение в проект {project_name}",
            message=f"{inviter_name} пригласил вас присоединиться к проекту",
            notification_metadata={
                "project_id": project_id,
                "project_name": project_name,
                "inviter_id": inviter_id,
                "inviter_name": inviter_name
            }
        )

    async def cleanup_old_notifications(self) -> int:
        """Удаляет старые уведомления"""
        return await self.repository.cleanup_old_notifications()