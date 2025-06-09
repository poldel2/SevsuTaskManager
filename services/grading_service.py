from typing import Optional
from models.domain.tasks import TaskGrade, TaskStatus, TaskCompletionStatus
from models.schemas.tasks import TaskGradeUpdate, ProjectGradingSettings
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

    async def get_user_tasks_for_grading(self, project_id: int, user_id: int) -> dict:
        stats = {
            'easy_completed': 0,
            'medium_completed': 0,
            'hard_completed': 0,
            'tasks': []
        }
        
        tasks = await self.grading_repository.get_project_tasks_for_user(project_id, user_id)
        
        for task in tasks:
            completion_value = 1.0 if task.completion_status == TaskCompletionStatus.COMPLETED else 0.5 if task.completion_status == TaskCompletionStatus.PARTIAL else 0
            
            if task.grade == TaskGrade.EASY:
                stats['easy_completed'] += completion_value
            elif task.grade == TaskGrade.MEDIUM:
                stats['medium_completed'] += completion_value
            elif task.grade == TaskGrade.HARD:
                stats['hard_completed'] += completion_value
            
            stats['tasks'].append({
                'id': task.id,
                'title': task.title,
                'grade': task.grade,
                'completion_status': task.completion_status,
                'project_id': task.project_id
            })
        
        settings = await self.grading_repository.get_grading_settings(project_id)
        if settings:
            stats['settings'] = {
                'required_easy_tasks': settings.required_easy_tasks,
                'required_medium_tasks': settings.required_medium_tasks,
                'required_hard_tasks': settings.required_hard_tasks
            }
        
        return stats

    async def update_task_grade(self, task_id: int, grade_data: TaskGradeUpdate) -> dict:
        grade_scores = {
            TaskGrade.HARD: 50,
            TaskGrade.MEDIUM: 25,
            TaskGrade.EASY: 10
        }
        
        score = grade_scores.get(grade_data.grade, 0)
        
        if grade_data.completion_status == TaskCompletionStatus.PARTIAL:
            score /= 2
        elif grade_data.completion_status == TaskCompletionStatus.NOT_COMPLETED:
            score = 0

        status_enum = TaskCompletionStatus(grade_data.completion_status)

        task = await self.grading_repository.update_task_grade(task_id, status_enum, score)
        return {
            "id": task.id,
            "completion_status": task.completion_status,
            "score": task.score,
        }

    async def get_grading_settings(self, project_id: int) -> dict:
        settings = await self.grading_repository.get_grading_settings(project_id)
        if not settings:
            return None
        return {
            "required_easy_tasks": settings.required_easy_tasks,
            "required_medium_tasks": settings.required_medium_tasks,
            "required_hard_tasks": settings.required_hard_tasks
        }

    async def save_grading_settings(self, project_id: int, settings: ProjectGradingSettings) -> None:
        await self.grading_repository.save_grading_settings(project_id, settings.dict())
