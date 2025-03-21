from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload

from models.domain.projects import Project
from models.domain.users import User
from models.domain.user_project import user_project_table, Role  # Убедитесь, что импорт правильный
from models.schemas.users import UserResponse


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
            .where(Project.id == project_id)
            .options(
                joinedload(Project.owner),
                joinedload(Project.users),
            )
        )
        return result.unique().scalar_one_or_none()

    async def get_all_for_user(self, user_id: int) -> Sequence[Project]:
        result = await self.session.execute(
            select(Project)
            .join(user_project_table, user_project_table.c.project_id == Project.id)  # Условие соединения
            .where(user_project_table.c.user_id == user_id)
            .options(
                joinedload(Project.owner),
                joinedload(Project.users),
            )
        )
        return result.unique().scalars().all()

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
            delete(user_project_table).where(user_project_table.c.project_id == project_id)
        )
        await self.session.execute(
            delete(Project).where(Project.id == project_id)
        )
        await self.session.commit()

    async def add_user_to_project(self, project_id: int, user_id: int, role: str) -> None:
        try:
            role_enum = Role[role.upper()]
        except KeyError:
            raise ValueError(f"Invalid role: {role}. Must be one of: {', '.join(r.name for r in Role)}")
        stmt = insert(user_project_table).values(
            user_id=user_id,
            project_id=project_id,
            role=role_enum
        ).on_conflict_do_nothing()
        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_user_from_project(self, project_id: int, user_id: int) -> None:
        await self.session.execute(
            delete(user_project_table)
            .where(user_project_table.c.project_id == project_id)
            .where(user_project_table.c.user_id == user_id)
        )
        await self.session.commit()

    async def get_project_users(self, project_id: int) -> Sequence[UserResponse]:
        result = await self.session.execute(
            select(UserResponse)
            .where(user_project_table.c.project_id == project_id)
        )
        return result.unique().scalars().all()