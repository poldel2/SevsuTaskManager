from typing import Optional
from models.domain.tasks import TaskGrade, TaskStatus
from repositories.grading_repository import GradingRepository

class GradingService:
    def __init__(self, grading_repository: GradingRepository):
        self.grading_repository = grading_repository

    async def update_user_progress(self, task, user_id: int) -> None:
        if task.status not in [TaskStatus.APPROVED_BY_LEADER.value, TaskStatus.APPROVED_BY_TEACHER.value]:
            return

        if not task.assignee_id:
            return  # Can't update progress if no assignee
            
        # Get progress for the assignee (not the approver)
        progress = await self.grading_repository.get_user_progress(
            task.assignee_id,
            task.project_id
        )

        progress_data = {
            "user_id": task.assignee_id,  # Use assignee's ID
            "project_id": task.project_id,
            "completed_easy": (progress.completed_easy if progress else 0) + (1 if task.grade == TaskGrade.EASY.value else 0),
            "completed_medium": (progress.completed_medium if progress else 0) + (1 if task.grade == TaskGrade.MEDIUM.value else 0),
            "completed_hard": (progress.completed_hard if progress else 0) + (1 if task.grade == TaskGrade.HARD.value else 0),
        }

        progress = await self.grading_repository.create_or_update_progress(progress_data)
        await self.calculate_auto_grade(progress)

    async def calculate_auto_grade(self, progress) -> Optional[str]:
        settings = await self.grading_repository.get_grading_settings(progress.project_id)
        if not settings:
            return None

        meets_easy = progress.completed_easy >= settings.required_easy_tasks
        meets_medium = progress.completed_medium >= settings.required_medium_tasks
        meets_hard = progress.completed_hard >= settings.required_hard_tasks

        if meets_easy and meets_medium and meets_hard:
            grade = "A"
        elif meets_easy and meets_medium:
            grade = "B"
        elif meets_easy:
            grade = "C"
        else:
            grade = "Fail"

        progress.auto_grade = grade
        await self.grading_repository.session.commit()
        return grade

    async def get_participants_progress(self, project_id: int) -> list[dict]:
        """
        Get progress report for all project participants
        """
        # Get progress for all participants from repository
        progress_records = await self.grading_repository.get_project_progress(project_id)
        
        # Format the report data
        report = []
        for progress in progress_records:
            user = progress.user
            report.append({
                "user_id": user.id,
                "user_name": f"{user.last_name} {user.first_name}",
                "completed_easy": progress.completed_easy,
                "completed_medium": progress.completed_medium,
                "completed_hard": progress.completed_hard,
                "auto_grade": progress.auto_grade,
                "manual_grade": progress.manual_grade
            })
            
        return report
    
    async def set_manual_grade(self, user_id: int, project_id: int, grade: str) -> None:
        """
        Set manual grade for a user in a project
        """
        progress = await self.grading_repository.get_user_progress(user_id, project_id)
        if not progress:
            # Create a new progress record if it doesn't exist
            progress_data = {
                "user_id": user_id,
                "project_id": project_id,
                "completed_easy": 0,
                "completed_medium": 0,
                "completed_hard": 0,
                "manual_grade": grade
            }
            await self.grading_repository.create_or_update_progress(progress_data)
        else:
            # Update existing progress record
            progress.manual_grade = grade
            await self.grading_repository.session.commit()
