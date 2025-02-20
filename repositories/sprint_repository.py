from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from models.domain.sprints import Sprint

class SprintRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, sprint_data: dict) -> Sprint:
        sprint = Sprint(**sprint_data)
        self.session.add(sprint)
        await self.session.commit()
        await self.session.refresh(sprint)
        return sprint

    async def get_by_id(self, sprint_id: int) -> Sprint | None:
        result = await self.session.execute(
            select(Sprint)
            .options(
                selectinload(Sprint.project),
                selectinload(Sprint.tasks)
            )
            .where(Sprint.id == sprint_id)
        )
        return result.scalar_one_or_none()

    async def get_for_project(self, project_id: int) -> list[Sprint]:
        result = await self.session.execute(
            select(Sprint)
            .options(selectinload(Sprint.tasks))
            .where(Sprint.project_id == project_id)
        )
        return result.scalars().all()

    async def update(self, sprint_id: int, update_data: dict) -> Sprint | None:
        await self.session.execute(
            update(Sprint)
            .where(Sprint.id == sprint_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(sprint_id)

    async def delete(self, sprint_id: int) -> None:
        await self.session.execute(
            delete(Sprint).where(Sprint.id == sprint_id)
        )
        await self.session.commit()