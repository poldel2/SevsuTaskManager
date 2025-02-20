from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from models.domain.sprints import Sprint
from repositories.sprint_repository import SprintRepository
from repositories.project_repository import ProjectRepository
from models.schemas.sprints import SprintResponse

class SprintService:
    def __init__(self, sprint_repository: SprintRepository, project_repo: ProjectRepository):
        self.sprint_repository = sprint_repository
        self.project_repo = project_repo

    async def _validate_project_access(self, project_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to project"
            )

    async def create_sprint(self, sprint_data: dict, user_id: int) -> SprintResponse:
        await self._validate_project_access(sprint_data["project_id"], user_id)
        sprint = await self.sprint_repository.create(sprint_data)
        # Предварительная загрузка связанных объектов
        query = await self.sprint_repository.session.execute(
            select(Sprint).options(selectinload(Sprint.project)).filter_by(id=sprint.id)
        )
        sprint = query.scalar_one()
        return SprintResponse.model_validate(sprint)

    async def get_sprint(self, sprint_id: int, user_id: int) -> SprintResponse:
        sprint = await self.sprint_repository.get_by_id(sprint_id)
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint not found")
        await self._validate_project_access(sprint.project_id, user_id)
        query = await self.sprint_repository.session.execute(
            select(Sprint).options(selectinload(Sprint.project)).filter_by(id=sprint.id)
        )
        sprint = query.scalar_one()
        return SprintResponse.model_validate(sprint)

    async def get_project_sprints(self, project_id: int, user_id: int) -> list[SprintResponse]:
        await self._validate_project_access(project_id, user_id)
        sprints = await self.sprint_repository.get_for_project(project_id)
        return [SprintResponse.model_validate(s) for s in sprints]

    async def update_sprint(self, sprint_id: int, update_data: dict, user_id: int) -> SprintResponse:
        sprint = await self.get_sprint(sprint_id, user_id)
        updated = await self.sprint_repository.update(sprint_id, update_data)
        return SprintResponse.model_validate(updated)

    async def delete_sprint(self, sprint_id: int, user_id: int) -> None:
        await self.get_sprint(sprint_id, user_id)
        await self.sprint_repository.delete(sprint_id)