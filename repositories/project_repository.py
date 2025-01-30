from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload

from models.domain.projects import Project
from models.domain.users import User


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_data: dict) -> Project:
        project = Project(**project_data)
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> Project | None:
        result = await self.session.execute(
            select(Project)
            .join(User)
            .where(Project.id == project_id)
            .options(joinedload(Project.owner))
        )
        return result.scalar_one_or_none()

    async def get_all_for_user(self, user_id: int) -> Sequence[Project]:
        result = await self.session.execute(
            select(Project)
            .join(User)
            .where(User.id == user_id)
            .options(joinedload(Project.owner))
        )
        return result.scalars().all()

    async def update(self, project_id: int, update_data: dict) -> Project | None:
        await self.session.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(project_id)

    async def delete(self, project_id: int) -> None:
        await self.session.execute(
            delete(Project).where(Project.id == project_id)
        )
        await self.session.commit()

