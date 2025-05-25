from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.domain.task_columns import TaskColumn
from models.domain.tasks import Task, TaskStatus, TaskGrade
from models.domain.users import User
from repositories.task_repository import TaskRepository
from repositories.project_repository import ProjectRepository
from repositories.sprint_repository import SprintRepository
from models.schemas.tasks import TaskResponse
from services.grading_service import GradingService
from services.notification_service import NotificationService, NotificationObserver
from models.domain.notifications import NotificationType
from services.activity_service import ActivityService, EntityType, ActionType


class TaskService:
    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
        sprint_repository: SprintRepository,
        grading_service: GradingService,
        notification_observer: NotificationObserver,
        activity_service: ActivityService
    ):
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.sprint_repository = sprint_repository
        self.grading_service = grading_service
        self.notification_observer = notification_observer
        self.activity_service = activity_service

    async def validate_project_access(self, project_id: int, user_id: int):
        project = await self.project_repository.get_by_id(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to project"
            )

    async def create_task(self, task_data: dict, user_id: int) -> TaskResponse:
        await self.validate_project_access(task_data["project_id"], user_id)

        if task_data.get("sprint_id"):
            sprint = await self.sprint_repository.get_by_id(task_data["sprint_id"])
            if not sprint or sprint.project_id != task_data["project_id"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sprint_id for the project"
                )

        if task_data.get("column_id"):
            column = await self.task_repository.session.execute(
                select(TaskColumn).where(TaskColumn.id == task_data["column_id"])
            )
            column = column.scalar_one_or_none()
            if not column or column.project_id != task_data["project_id"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid column_id for the project"
                )

        task = await self.task_repository.create(task_data)
        
        # Отправляем уведомление, если назначен исполнитель
        if task.assignee_id:
            project = await self.project_repository.get_by_id(task_data["project_id"])
            await self.notification_observer.on_task_assigned(
                user_id=task.assignee_id,
                task_id=task.id,
                task_title=task.title,
                project_id=task_data["project_id"],
                project_name=project.title
            )
        
        await self.activity_service.log_activity(
            project_id=task.project_id,
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=task.id,
            action=ActionType.CREATE,
            changes=task_data
        )

        task = await self.task_repository.get_by_id(task.id)
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: int, user_id: int) -> TaskResponse:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        await self.validate_project_access(task.project_id, user_id)
        return TaskResponse.model_validate(task)

    async def get_tasks_by_project(self, project_id: int, user_id: int) -> list[TaskResponse]:
        await self.validate_project_access(project_id, user_id)
        tasks = await self.task_repository.get_tasks_by_project(project_id)
        return [TaskResponse.model_validate(task) for task in tasks]

    async def get_tasks_by_sprint(self, sprint_id: int, user_id: int) -> list[TaskResponse]:
        sprint = await self.sprint_repository.get_by_id(sprint_id)
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint not found")

        await self.validate_project_access(sprint.project_id, user_id)
        tasks = await self.task_repository.get_tasks_by_sprint(sprint_id)
        return [TaskResponse.model_validate(task) for task in tasks]

    async def update_task(self, task_id: int, update_data: dict, user_id: int) -> TaskResponse:
        task = await self.get_task(task_id, user_id)
        if update_data.get("sprint_id"):
            sprint = await self.sprint_repository.get_by_id(update_data["sprint_id"])
            if not sprint or sprint.project_id != task.project.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid sprint_id for the project"
                )
        if update_data.get("column_id"):
            column = await self.task_repository.session.execute(
                select(TaskColumn).where(TaskColumn.id == update_data["column_id"])
            )
            column = column.scalar_one_or_none()
            if not column or column.project_id != task.project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid column_id for the project"
                )
        updated = await self.task_repository.update(task_id, update_data)
        task_response = TaskResponse.model_validate(task)
        updated_response = TaskResponse.model_validate(updated)

        await self.activity_service.log_activity(
            project_id=updated.project_id,
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=task_id,
            action=ActionType.UPDATE,
            changes={
                "old": task_response.model_dump(),
                "new": updated_response.model_dump(),
                "changed_fields": update_data
            }
        )

        return updated_response

    async def update_task_partial(
            self,
            task_id: int,
            update_data: dict,
            user_id: int
    ) -> TaskResponse:
        task = await self.get_task(task_id, user_id)

        if "status" in update_data:
            new_status = update_data["status"]
            # Проверка прав на изменение статуса
            if new_status == TaskStatus.APPROVED_BY_LEADER.value:
                if not await self._is_project_leader(user_id, task.project_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only project leaders can approve tasks"
                    )
                if task.grade == TaskGrade.HARD.value:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Hard tasks can only be approved by teacher"
                    )

            if new_status == TaskStatus.APPROVED_BY_TEACHER.value:
                if not await self._is_teacher(user_id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Only teachers can perform this action"
                    )

        # Если изменяется assignee_id
        old_assignee_id = task.assignee_id
        new_assignee_id = update_data.get('assignee_id')
        
        if new_assignee_id and new_assignee_id != old_assignee_id:
            project = await self.project_repository.get_by_id(task.project_id)
            await self.notification_observer.on_task_assigned(
                user_id=new_assignee_id,
                task_id=task.id,
                task_title=task.title,
                project_id=project.id,
                project_name=project.title
            )

        updated = await self.task_repository.update_partial(task_id, update_data)
        task_response = TaskResponse.model_validate(task)
        updated_response = TaskResponse.model_validate(updated)

        if "status" in update_data and update_data["status"] in [
            TaskStatus.APPROVED_BY_LEADER.value,
            TaskStatus.APPROVED_BY_TEACHER.value
        ]:
            await self.grading_service.update_user_progress(updated, updated.assignee_id)

        changes = {
            "old": task_response.model_dump(),
            "new": updated_response.model_dump(),
            "changed_fields": update_data
        }

        await self.activity_service.log_activity(
            project_id=updated.project_id,
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=task_id,
            action=ActionType.UPDATE,
            changes=changes
        )

        return updated_response

    async def delete_task(self, task_id: int, user_id: int) -> None:
        task = await self.get_task(task_id, user_id)
        task_response = TaskResponse.model_validate(task)
        await self.task_repository.delete(task_id)

        await self.activity_service.log_activity(
            project_id=task.project_id,
            user_id=user_id,
            entity_type=EntityType.TASK,
            entity_id=task_id,
            action=ActionType.DELETE,
            changes={"task": task_response.model_dump()}
        )

    async def _is_project_leader(self, user_id: int, project_id: int) -> bool:
        user = await self.task_repository.session.get(User, user_id)
        return user.is_project_leader(project_id)

    async def _is_teacher(self, user_id: int) -> bool:
        user = await self.task_repository.session.get(User, user_id)
        return user.is_teacher

    async def assign_task(self, task_id: int, assignee_id: int) -> Task:
        task = await self.task_repository.assign_task(task_id, assignee_id)
        if task and task.project:
            await self.notification_observer.on_task_assigned(
                user_id=assignee_id,
                task_id=task.id,
                task_title=task.title,
                project_id=task.project.id,
                project_name=task.project.name
            )
        return task

    async def update_task_status(self, task_id: int, status: str) -> Task:
        task = await self.task_repository.update_task_status(task_id, status)
        if task and task.assignee_id:
            await self.notification_observer.on_task_status_updated(
                user_id=task.assignee_id,
                task_id=task.id,
                task_title=task.title,
                project_id=task.project.id,
                project_name=task.project.name,
                status=status
            )
        return task

    async def get_related_tasks(self, task_id: int, user_id: int) -> list[TaskResponse]:
        task = await self.task_repository.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        await self.validate_project_access(task.project_id, user_id)
        related_tasks = await self.task_repository.get_related_tasks(task_id)
        return [TaskResponse.model_validate(task) for task in related_tasks]