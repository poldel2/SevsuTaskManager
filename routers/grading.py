from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user
from dependencies import get_grading_service, get_project_service
from models.schemas.users import UserResponse
from models.schemas.tasks import TaskGradeUpdate, ProjectGradingSettings
from services.grading_service import GradingService
from services.project_service import ProjectService

router = APIRouter(prefix="/grading", tags=["grading"])

@router.get("/projects/{project_id}/users/{user_id}/tasks")
async def get_user_tasks_for_grading(
    project_id: int,
    user_id: int,
    service: GradingService = Depends(get_grading_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user: UserResponse = Depends(get_current_user)
):
    project = await project_service.get_project(project_id, user_id)
    if not any(user.id == user_id for user in project.users):
        raise HTTPException(status_code=404, detail="User not found in project")
    
    return await service.get_user_tasks_for_grading(project_id, user_id)

@router.post("/tasks/{task_id}/grade")
async def update_task_grade(
    task_id: int,
    grade_data: TaskGradeUpdate,
    service: GradingService = Depends(get_grading_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.update_task_grade(task_id, grade_data)

@router.get("/projects/{project_id}/settings")
async def get_grading_settings(
    project_id: int,
    service: GradingService = Depends(get_grading_service),
    current_user: UserResponse = Depends(get_current_user)
):
    settings = await service.get_grading_settings(project_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Grading settings not found")
    return settings

@router.put("/projects/{project_id}/settings")
async def update_grading_settings(
    project_id: int,
    settings: ProjectGradingSettings,
    service: GradingService = Depends(get_grading_service),
    current_user: UserResponse = Depends(get_current_user)
):
    await service.save_grading_settings(project_id, settings)