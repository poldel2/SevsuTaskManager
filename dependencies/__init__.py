from fastapi import Depends
from repositories.grading_repository import GradingRepository
from repositories.project_repository import ProjectRepository
from repositories.sprint_repository import SprintRepository
from repositories.task_column_repository import TaskColumnRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from repositories.message_repository import MessageRepository
from repositories.notification_repository import NotificationRepository
from repositories.activity_repository import ActivityRepository
from services.auth_service import AuthService
from services.grading_service import GradingService
from services.message_service import MessageService
from services.notification_service import NotificationService
from services.notification_manager import NotificationManager
from services.project_service import ProjectService
from services.sprint_service import SprintService
from services.task_column_service import TaskColumnService
from services.task_service import TaskService
from services.activity_service import ActivityService
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

_notification_manager = NotificationManager()

def get_notification_manager() -> NotificationManager:
    return _notification_manager

async def get_auth_service(
    session: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(UserRepository(session))

async def get_notification_repository(db: AsyncSession = Depends(get_db)):
    return NotificationRepository(db)

async def get_notification_service(
    session: AsyncSession = Depends(get_db),
    manager: NotificationManager = Depends(get_notification_manager)
) -> NotificationService:
    notification_repo = NotificationRepository(session)
    return NotificationService(notification_repo, manager)

async def get_activity_service(
    db: AsyncSession = Depends(get_db)
) -> ActivityService:
    activity_repo = ActivityRepository(db)
    user_repo = UserRepository(db)
    column_repo = TaskColumnRepository(db)
    return ActivityService(activity_repo, user_repo, column_repo)

async def get_project_service(
    session: AsyncSession = Depends(get_db),
    notification_service: NotificationService = Depends(get_notification_service)
) -> ProjectService:
    project_repo = ProjectRepository(session)
    column_repo = TaskColumnRepository(session)
    return ProjectService(project_repo, notification_service, column_repo)

async def get_sprint_service(
    session: AsyncSession = Depends(get_db)
) -> SprintService:
    sprint_repo = SprintRepository(session)
    project_repo = ProjectRepository(session)
    return SprintService(sprint_repo, project_repo)

async def get_task_service(
    session: AsyncSession = Depends(get_db),
    notification_observer: NotificationService = Depends(get_notification_service),
    activity_service: ActivityService = Depends(get_activity_service)
) -> TaskService:
    task_repo = TaskRepository(session)
    project_repo = ProjectRepository(session)
    sprint_repo = SprintRepository(session)
    grading_repo = GradingRepository(session)
    grading_service = GradingService(grading_repo)
    
    return TaskService(
        task_repo, 
        project_repo, 
        sprint_repo, 
        grading_service,
        notification_observer,
        activity_service
    )

def get_message_service(
    session: AsyncSession = Depends(get_db)
) -> MessageService:
    message_repo = MessageRepository(session)
    project_repo = ProjectRepository(session)
    user_repo = UserRepository(session)
    return MessageService(message_repo, project_repo, user_repo)

def get_task_column_service(
    session: AsyncSession = Depends(get_db)
) -> TaskColumnService:
    column_repo = TaskColumnRepository(session)
    project_repo = ProjectRepository(session)
    return TaskColumnService(column_repo, project_repo)

def get_grading_service(
    session: AsyncSession = Depends(get_db)
) -> GradingService:
    grading_repo = GradingRepository(session)
    return GradingService(grading_repo)