from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from models.domain.tasks import Task

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task_data: dict) -> Task:
        task = Task(**task_data)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.session.execute(
            select(Task)
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint),
                selectinload(Task.assignee),  # Загружаем данные о пользователе
            )
            .where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_tasks_by_project(self, project_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint),
                selectinload(Task.assignee),
            )
            .where(Task.project_id == project_id)
        )
        return result.scalars().all()

    async def get_tasks_by_sprint(self, sprint_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint),
                selectinload(Task.assignee),
            )
            .where(Task.sprint_id == sprint_id)
        )
        return result.scalars().all()

    async def update(self, task_id: int, update_data: dict) -> Task | None:
        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(task_id)

    async def update_partial(self, task_id: int, update_data: dict) -> Task | None:
        if not update_data:
            return await self.get_by_id(task_id)

        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
        )
        await self.session.commit()
        return await self.get_by_id(task_id)

    async def delete(self, task_id: int) -> None:
        await self.session.execute(
            delete(Task).where(Task.id == task_id)
        )
        await self.session.commit()
