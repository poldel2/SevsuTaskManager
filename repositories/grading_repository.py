from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.domain.tasks import UserProjectProgress, ProjectGradingSettings


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

    async def get_grading_settings(self, project_id: int) -> ProjectGradingSettings | None:
        result = await self.session.execute(
            select(ProjectGradingSettings)
            .where(ProjectGradingSettings.project_id == project_id)
        )
        return result.scalar_one_or_none()

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
