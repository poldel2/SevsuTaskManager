from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from models.domain.task_columns import TaskColumn

class TaskColumnRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, column_data: dict) -> TaskColumn:
        column = TaskColumn(**column_data)
        self.session.add(column)
        await self.session.commit()
        await self.session.refresh(column)
        return column

    async def get_by_project(self, project_id: int) -> Sequence[TaskColumn]:
        result = await self.session.execute(
            select(TaskColumn)
            .where(TaskColumn.project_id == project_id)
            .order_by(TaskColumn.position, TaskColumn.id)
        )
        return result.scalars().all()

    async def update(self, column_id: int, update_data: dict) -> TaskColumn | None:
        await self.session.execute(
            update(TaskColumn)
            .where(TaskColumn.id == column_id)
            .values(**update_data)
        )
        await self.session.commit()
        result = await self.session.execute(select(TaskColumn).where(TaskColumn.id == column_id))
        return result.scalar_one_or_none()

    async def delete(self, column_id: int) -> None:
        await self.session.execute(
            delete(TaskColumn).where(TaskColumn.id == column_id)
        )
        await self.session.commit()