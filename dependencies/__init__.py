from fastapi import Depends

from repositories.grading_repository import GradingRepository
from repositories.project_repository import ProjectRepository
from repositories.sprint_repository import SprintRepository
from repositories.task_column_repository import TaskColumnRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.message_repository import MessageRepository
from services.grading_service import GradingService
from services.message_service import MessageService

from services.project_service import ProjectService
from services.sprint_service import SprintService
from services.task_column_service import TaskColumnService
from services.task_service import TaskService


async def get_auth_service(
    session: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(UserRepository(session))

async def get_project_service(
    session: AsyncSession = Depends(get_db)
) -> ProjectService:
    column_repo = TaskColumnRepository(session)
    repo = ProjectRepository(session)
    return ProjectService(repo, column_repo)

async def get_sprint_service(
    session: AsyncSession = Depends(get_db)
) -> SprintService:
    sprint_repo = SprintRepository(session)
    project_repo = ProjectRepository(session)
    return SprintService(sprint_repo, project_repo)


def get_task_service(
        session: AsyncSession = Depends(get_db)
) -> TaskService:
    task_repo = TaskRepository(session)
    sprint_repo = SprintRepository(session)
    project_repo = ProjectRepository(session)
    grading_service = get_grading_service(session)
    return TaskService(task_repo, project_repo, sprint_repo, grading_service)


message_service_instance = MessageService(
    message_repository=MessageRepository(None),
    project_repository=ProjectRepository(None),
    user_repository=UserRepository(None)
)

def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    message_service_instance.message_repository.session = db
    message_service_instance.project_repository.session = db
    message_service_instance.user_repository.session = db
    return message_service_instance

def get_task_column_service(session: AsyncSession = Depends(get_db)) -> TaskColumnService:
    column_repo = TaskColumnRepository(session)
    project_repo = ProjectRepository(session)
    return TaskColumnService(column_repo, project_repo)

def get_grading_service(session: AsyncSession = Depends(get_db)) -> GradingService:
    grading_repo = GradingRepository(session)
    return GradingService(grading_repo)