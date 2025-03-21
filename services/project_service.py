from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models.domain.projects import Project
from models.schemas.projects import ProjectCreate, ProjectUpdate
from repositories.project_repository import ProjectRepository
from repositories.task_column_repository import TaskColumnRepository


class ProjectService:
    def __init__(self, repository: ProjectRepository, column_repo: TaskColumnRepository):
        self.repository = repository
        self.column_repo = column_repo

    async def create_project(self, project_data: dict, owner_id: int) -> Project:
        project = await self.repository.create({
            **project_data,
            "owner_id": owner_id
        })
        default_columns = [
            {"name": "К выполнению", "project_id": project.id, "position": 0, "color": "#b3b3b3"},
            {"name": "Выполнить", "project_id": project.id, "position": 1, "color": "#fabd06"},
            {"name": "Готово", "project_id": project.id, "position": 2, "color": "#22b622"},
        ]
        for column_data in default_columns:
            await self.column_repo.create(column_data)

        await self.repository.add_user_to_project(project.id, owner_id, "OWNER")
        return project

    async def get_user_projects(self, user_id: int) -> Sequence[Project]:
        projects = await self.repository.get_all_for_user(user_id)
        if not projects:
            return []
        return projects

    async def get_project(self, project_id: int, user_id: int) -> Optional[Project]:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        # Проверяем, является ли пользователь участником проекта
        user_ids = [u.id for u in project.users]
        if user_id not in user_ids and project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project"
            )
        return project

    async def get_all_projects(self, user_id: int) -> Sequence[Project]:
        return await self.repository.get_all_for_user(user_id)

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        user_id: int
    ) -> Project:
        project = await self.get_project(project_id, user_id)
        # Только владелец может обновлять проект
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update it"
            )
        return await self.repository.update(project_id, project_data.model_dump(exclude_unset=True))

    async def delete_project(self, project_id: int, user_id: int) -> None:
        project = await self.get_project(project_id, user_id)
        # Только владелец может удалять проект
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can delete it"
            )
        await self.repository.delete(project_id)

    async def add_user_to_project(self, project_id: int, user_id: int, role: str, current_user_id: int) -> None:
        project = await self.get_project(project_id, current_user_id)
        # Только владелец может добавлять участников
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can add users"
            )
        await self.repository.add_user_to_project(project_id, user_id, role)

    async def remove_user_from_project(self, project_id: int, user_id: int, current_user_id: int) -> None:
        project = await self.get_project(project_id, current_user_id)
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can remove users"
            )
        if user_id == project.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove project owner"
            )
        await self.repository.remove_user_from_project(project_id, user_id)

    async def get_project_users(self, project_id: int, user_id: int) -> Sequence[dict]:
        await self.get_project(project_id, user_id)  # Проверка доступа
        return await self.repository.get_project_users(project_id)