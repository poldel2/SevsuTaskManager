from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from models.domain.projects import Project
from models.schemas.projects import ProjectCreate, ProjectUpdate, Project
from repositories.project_repository import ProjectRepository
from fastapi import HTTPException, status

class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def create_project(self, project_data: dict, owner_id: int) -> Project:
        project = await self.repository.create({
            **project_data,
            "owner_id": owner_id
        })
        return project

    async def get_user_projects(self, user_id: int) -> Sequence[Project]:
        return await self.repository.get_all_for_user(user_id)

    async def get_project(self, project_id: int, owner_id: int) -> Optional[Project]:
        project = await self.repository.get_by_id(project_id)
        if not project or project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project

    async def get_all_projects(self, owner_id: int) -> Sequence[Project]:
        return await self.repository.get_all_for_user(owner_id)

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        owner_id: int
    ) -> Project:
        project = await self.get_project(project_id, owner_id)
        return await self.repository.update(project_id, project_data.model_dump())

    async def delete_project(self, project_id: int, owner_id: int) -> None:
        await self.get_project(project_id, owner_id)
        await self.repository.delete(project_id)