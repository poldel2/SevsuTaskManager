from fastapi import Depends

from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from services.project_service import ProjectService


async def get_auth_service(
    session: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(UserRepository(session))

async def get_project_service(
    session: AsyncSession = Depends(get_db)
) -> ProjectService:
    repo = ProjectRepository(session)
    return ProjectService(repo)