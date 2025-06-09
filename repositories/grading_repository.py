from repositories.task_repository import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from models.domain.tasks import TaskCompletionStatus, UserProjectProgress, ProjectGradingSettings, Task


class GradingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_progress(self, user_id: int, project_id: int) -> UserProjectProgress | None:
        result = await self.session.execute(
            select(UserProjectProgress)
            .where(
                UserProjectProgress.user_id == user_id,
                UserProjectProgress.project_id == project_id
            )
        )
        return result.scalar_one_or_none()

    async def get_project_tasks_for_user(self, project_id: int, user_id: int) -> list[Task]:
        result = await self.session.execute(
            select(Task).where(
                and_(
                    Task.project_id == project_id,
                    Task.assignee_id == user_id
                )
            )
        )
        return result.scalars().all()

    async def update_task_grade(self, task_id: int, completion_status: TaskCompletionStatus, score: float) -> Task | None:
        update_data = {
            "completion_status": completion_status,
            "score": score
        }
        await self.session.execute(
            update(Task)
            .where(Task.id == task_id)
            .values(**update_data)
        )
        await self.session.commit()
        task_repository = TaskRepository(self.session)
        return await task_repository.get_by_id(task_id)

    async def get_grading_settings(self, project_id: int) -> ProjectGradingSettings | None:
        result = await self.session.execute(
            select(ProjectGradingSettings)
            .where(ProjectGradingSettings.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def save_grading_settings(self, project_id: int, settings: dict) -> None:
        progress = await self.get_grading_settings(project_id)
        if not progress:
            progress = ProjectGradingSettings(project_id=project_id, **settings)
            self.session.add(progress)
        else:
            for key, value in settings.items():
                setattr(progress, key, value)
        await self.session.commit()

    async def create_or_update_progress(self, progress_data: dict) -> UserProjectProgress:
        progress = await self.get_user_progress(
            progress_data["user_id"],
            progress_data["project_id"]
        )

        if not progress:
            progress = UserProjectProgress(**progress_data)
            self.session.add(progress)
        else:
            for key, value in progress_data.items():
                setattr(progress, key, value)

        await self.session.commit()
        await self.session.refresh(progress)
        return progress

    async def get_project_progress(self, project_id: int) -> list[UserProjectProgress]:
        """
        Get progress for all participants in a project
        """
        result = await self.session.execute(
            select(UserProjectProgress)
            .where(UserProjectProgress.project_id == project_id)
            .join(UserProjectProgress.user)  # Join with User model
        )
        return result.scalars().all()
