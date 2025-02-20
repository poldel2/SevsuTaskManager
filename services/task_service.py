from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.domain.tasks import Task
from repositories.task_repository import TaskRepository
from repositories.project_repository import ProjectRepository
from repositories.sprint_repository import SprintRepository
from models.schemas.tasks import TaskResponse

class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
        sprint_repository: SprintRepository
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.sprint_repository = sprint_repository

    async def _validate_project_access(self, project_id: int, user_id: int):
        project = await self.project_repository.get_by_id(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to project"
            )

    async def create_task(self, task_data: dict, user_id: int) -> TaskResponse:
        # Проверка доступа к проекту
        await self._validate_project_access(task_data["project_id"], user_id)

        # Если передан sprint_id, проверяем, что спринт принадлежит этому проекту
        if task_data.get("sprint_id"):
            sprint = await self.sprint_repository.get_by_id(task_data["sprint_id"])
            if not sprint or sprint.project_id != task_data["project_id"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sprint_id for the project"
                )

        task = await self.task_repository.create(task_data)

        # Предварительная загрузка связанных объектов для корректной валидации схемой
        query = await self.task_repository.session.execute(
            select(Task)
            .options(
                selectinload(Task.project),
                selectinload(Task.sprint)
            )
            .filter_by(id=task.id)
        )
        task = query.scalar_one()
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: int, user_id: int) -> TaskResponse:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        await self._validate_project_access(task.project_id, user_id)

        return TaskResponse.model_validate({
            **task.__dict__,
            "assignee_name": task.assignee.last_name if task.assignee else None,  # Передаём имя пользователя
        })

    async def get_tasks_by_project(self, project_id: int, user_id: int) -> list[TaskResponse]:
        await self._validate_project_access(project_id, user_id)

        tasks = await self.task_repository.get_tasks_by_project(project_id)

        return [
            TaskResponse.model_validate({
                **task.__dict__,
                "assignee_name": task.assignee.last_name if task.assignee else None,
            })
            for task in tasks
        ]

    async def get_tasks_by_sprint(self, sprint_id: int, user_id: int) -> list[TaskResponse]:
        sprint = await self.sprint_repository.get_by_id(sprint_id)
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint not found")

        await self._validate_project_access(sprint.project_id, user_id)

        tasks = await self.task_repository.get_tasks_by_sprint(sprint_id)

        return [
            TaskResponse.model_validate({
                **task.__dict__,
                "assignee_name": task.assignee.last_name if task.assignee else None,
            })
            for task in tasks
        ]

    async def update_task(self, task_id: int, update_data: dict, user_id: int) -> TaskResponse:
        # Получаем задачу для валидации доступа
        task = await self.get_task(task_id, user_id)
        if update_data.get("sprint_id"):
            sprint = await self.sprint_repository.get_by_id(update_data["sprint_id"])
            if not sprint or sprint.project_id != task.project.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sprint_id for the project"
                )
        updated = await self.task_repository.update(task_id, update_data)
        return TaskResponse.model_validate(updated)

    async def update_task_partial(self, task_id: int, update_data: dict, user_id: int) -> TaskResponse:
        task = await self.get_task(task_id, user_id)

        if update_data.get("sprint_id"):
            sprint = await self.sprint_repository.get_by_id(update_data["sprint_id"])
            if not sprint or sprint.project_id != task.project.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sprint_id for the project"
                )

        updated = await self.task_repository.update_partial(task_id, update_data)
        return TaskResponse.model_validate(updated)

    async def delete_task(self, task_id: int, user_id: int) -> None:
        await self.get_task(task_id, user_id)
        await self.task_repository.delete(task_id)
