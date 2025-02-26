from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import joinedload

from models.domain.projects import Project
from models.domain.users import User
from models.domain.user_project import user_project_table

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
                joinedload(Project.owner),  # Загрузка владельца
                joinedload(Project.users),  # Загрузка связанных пользователей
            )
        )
        # Добавляем .unique() для устранения дубликатов из-за коллекций
        return result.unique().scalar_one_or_none()

    async def get_all_for_user(self, user_id: int) -> Sequence[Project]:
        result = await self.session.execute(
            select(Project)
            .join(user_project_table, user_project_table.c.project_id == Project.id)
            .where(user_project_table.c.user_id == user_id)
            .options(
                joinedload(Project.owner),
                joinedload(Project.users),
            )
        )
        # .unique() для коллекций перед .scalars()
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
        stmt = insert(user_project_table).values(
            user_id=user_id,
            project_id=project_id,
            role=role
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

    async def get_project_users(self, project_id: int) -> Sequence[dict]:
        result = await self.session.execute(
            select(user_project_table.c.user_id, user_project_table.c.role)
            .where(user_project_table.c.project_id == project_id)
        )
        return [{"user_id": row.user_id, "role": row.role} for row in result]