from fastapi import HTTPException, status
from typing import List, Sequence
from repositories.task_column_repository import TaskColumnRepository
from repositories.project_repository import ProjectRepository
from models.domain.task_columns import TaskColumn
from models.schemas.task_columns import TaskColumnCreate, TaskColumnUpdate


class TaskColumnService:
    def __init__(self, column_repo: TaskColumnRepository, project_repo: ProjectRepository):
        self.column_repo = column_repo
        self.project_repo = project_repo

    async def _check_project_access(self, project_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_users = await self.project_repo.get_project_users(project_id)
        if not any(user.id == user_id for user in project_users):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project"
            )

    async def get_by_project(self, project_id: int, user_id: int) -> Sequence[TaskColumn]:
        await self._check_project_access(project_id, user_id)
        columns = await self.column_repo.get_by_project(project_id)
        return columns

    async def create(self, project_id: int, column_data: TaskColumnCreate, user_id: int) -> TaskColumn:
        await self._check_project_access(project_id, user_id)
        column = await self.column_repo.create({"project_id": project_id, **column_data.model_dump()})
        return column

    async def update(self, project_id: int, column_id: int, column_data: TaskColumnUpdate, user_id: int) -> TaskColumn:
        await self._check_project_access(project_id, user_id)
        column = await self.column_repo.update(column_id, column_data.model_dump())
        if not column:
            raise HTTPException(status_code=404, detail="Column not found")
        return column

    async def delete(self, project_id: int, column_id: int, user_id: int) -> None:
        await self._check_project_access(project_id, user_id)
        await self.column_repo.delete(column_id)