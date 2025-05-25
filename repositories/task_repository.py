from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from models.domain.tasks import Task, TaskRelation, TaskRelationType

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
                selectinload(Task.assignee),
                selectinload(Task.column),
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
                selectinload(Task.column),
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
                selectinload(Task.column),
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

    async def get_related_tasks(self, task_id: int) -> list[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return []
            
        result = await self.session.execute(
            select(Task)
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint),
                selectinload(Task.assignee),
                selectinload(Task.column),
            )
            .where(
                Task.project_id == task.project_id,
                Task.sprint_id == task.sprint_id,
                Task.id != task_id
            )
        )
        return result.scalars().all()

    async def create_relation(self, relation_data: dict) -> TaskRelation:
        relation = TaskRelation(**relation_data)
        self.session.add(relation)
        await self.session.commit()
        await self.session.refresh(relation)
        return relation

    async def delete_relation(self, relation_id: int) -> None:
        await self.session.execute(
            delete(TaskRelation).where(TaskRelation.id == relation_id)
        )
        await self.session.commit()

    async def delete_relation_by_tasks(self, source_task_id: int, target_task_id: int) -> None:
        await self.session.execute(
            delete(TaskRelation).where(
                ((TaskRelation.source_task_id == source_task_id) & (TaskRelation.target_task_id == target_task_id)) |
                ((TaskRelation.source_task_id == target_task_id) & (TaskRelation.target_task_id == source_task_id))
            )
        )
        await self.session.commit()

    async def get_task_relations(self, task_id: int, relation_type: TaskRelationType = None) -> list[Task]:
        query = (
            select(Task)
            .distinct()
            .join(TaskRelation, 
                  ((TaskRelation.source_task_id == task_id) & (Task.id == TaskRelation.target_task_id)) |
                  ((TaskRelation.target_task_id == task_id) & (Task.id == TaskRelation.source_task_id))
            )
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint),
                selectinload(Task.assignee),
                selectinload(Task.column),
            )
        )

        if relation_type:
            query = query.where(TaskRelation.relation_type == relation_type)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_parent_task(self, task_id: int) -> Task | None:
        result = await self.session.execute(
            select(Task)
            .join(TaskRelation, 
                  (TaskRelation.source_task_id == Task.id) & 
                  (TaskRelation.target_task_id == task_id) & 
                  (TaskRelation.relation_type == TaskRelationType.PARENT)
            )
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint),
                selectinload(Task.assignee),
                selectinload(Task.column),
            )
        )
        return result.scalar_one_or_none()