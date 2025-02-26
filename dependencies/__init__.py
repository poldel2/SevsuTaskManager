from fastapi import Depends

from repositories.project_repository import ProjectRepository
from repositories.sprint_repository import SprintRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.message_repository import MessageRepository
from services.message_service import MessageService

from services.project_service import ProjectService
from services.sprint_service import SprintService
from services.task_service import TaskService


async def get_auth_service(
    session: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(UserRepository(session))

async def get_project_service(
    session: AsyncSession = Depends(get_db)
) -> ProjectService:
    repo = ProjectRepository(session)
    return ProjectService(repo)

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
    return TaskService(task_repo, project_repo, sprint_repo)


def get_message_service(session: AsyncSession = Depends(get_db)):
    message_repo = MessageRepository(session)
    project_repo = ProjectRepository(session)
    return MessageService(message_repo, project_repo)