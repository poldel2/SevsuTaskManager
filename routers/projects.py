from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from core.db import get_db
from models.schemas.activities import ActivityResponse
from services.project_service import ProjectService
from services.activity_service import ActivityService
from repositories.activity_repository import ActivityRepository

from models.domain.users import User
from models.schemas.projects import ProjectCreate, ProjectUpdate, Project
from dependencies import get_project_service, get_task_column_service, get_grading_service, get_activity_service
from core.security import get_current_user
from models.schemas.task_columns import TaskColumnUpdate, TaskColumnCreate, TaskColumn
from models.schemas.users import UserResponse
from services.project_service import ProjectService
from services.task_column_service import TaskColumnService
from services.grading_service import GradingService

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    project_data_dict = project_data.model_dump()
    return await service.create_project(project_data_dict, current_user.id)  # TODO:: заменить на current_user.id

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_project(project_id, current_user.id)  # TODO:: заменить на current_user.id

@router.get("/", response_model=list[Project])
async def get_all_projects(
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_all_projects(current_user.id)  # TODO:: заменить на current_user.id

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.update_project(project_id, project_data, current_user.id)  # TODO:: заменить на current_user.id

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_project(project_id, current_user.id)  # TODO:: заменить на current_user.id
    return {"message": "Project deleted"}

@router.post("/{project_id}/users/{user_id}", status_code=status.HTTP_201_CREATED)
async def add_user_to_project(
    project_id: int,
    user_id: int,
    role: str = "MEMBER",  # Роль по умолчанию
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    await service.add_user_to_project(project_id, user_id, role, current_user.id)  # TODO:: заменить на current_user.id
    return {"message": f"User {user_id} added to project {project_id} with role {role}"}

@router.delete("/{project_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_project(
    project_id: int,
    user_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    await service.remove_user_from_project(project_id, user_id, current_user.id)  # TODO:: заменить на current_user.id

@router.get("/{project_id}/users", response_model=list[UserResponse])
async def get_project_users(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_project_users(project_id, current_user.id)  # TODO:: заменить на current_user.id

@router.get("/{project_id}/columns", response_model=list[TaskColumn])
async def get_columns(
    project_id: int,
    column_service: TaskColumnService = Depends(get_task_column_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await column_service.get_by_project(project_id, current_user.id)

@router.post("/{project_id}/columns", response_model=TaskColumn, status_code=status.HTTP_201_CREATED)
async def create_column(
    project_id: int,
    column_data: TaskColumnCreate,
    column_service: TaskColumnService = Depends(get_task_column_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await column_service.create(project_id, column_data, current_user.id)

@router.put("/{project_id}/columns/{column_id}", response_model=TaskColumn)
async def update_column(
    project_id: int,
    column_id: int,
    column_data: TaskColumnUpdate,
    column_service: TaskColumnService = Depends(get_task_column_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await column_service.update(project_id, column_id, column_data, current_user.id)

@router.delete("/{project_id}/columns/{column_id}")
async def delete_column(
    project_id: int,
    column_id: int,
    column_service: TaskColumnService = Depends(get_task_column_service),
    current_user: UserResponse = Depends(get_current_user)
):
    await column_service.delete(project_id, column_id, current_user.id)
    return {"message": "Column deleted"}

@router.get("/{project_id}/reports/participants", response_model=list[dict])
async def get_project_participants_report(
    project_id: int,
    service: ProjectService = Depends(get_project_service),
    grading_service: GradingService = Depends(get_grading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get a report of all participants' progress in the project.
    Shows completed tasks by difficulty level and auto/manual grades.
    Only project leaders and teachers can access this endpoint.
    """
    # Check if user is project leader or teacher
    if not (current_user.is_teacher or await service._is_user_project_leader(current_user.id, project_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project leaders and teachers can access project reports"
        )
    
    return await grading_service.get_participants_progress(project_id)

@router.post("/{project_id}/participants/{user_id}/grade")
async def set_participant_manual_grade(
    project_id: int,
    user_id: int,
    grade: str,
    service: ProjectService = Depends(get_project_service),
    grading_service: GradingService = Depends(get_grading_service),
    current_user: User = Depends(get_current_user)
):
    """
    Set a manual grade for a project participant.
    Only project leaders and teachers can set grades.
    """
    # Check if user is project leader or teacher
    if not (current_user.is_teacher or await service._is_user_project_leader(current_user.id, project_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project leaders and teachers can set manual grades"
        )
    
    await grading_service.set_manual_grade(user_id, project_id, grade)
    return {"message": f"Manual grade set to {grade}"}

@router.get("/{project_id}/activities")
async def get_project_activities(
    project_id: int,
    offset: int = 0,
    limit: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    action: Optional[str] = None,
    service: ActivityService = Depends(get_activity_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_project_activities(
        project_id=project_id,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
        action=action
    )

@router.post("/{project_id}/logo")
async def upload_project_logo(
    project_id: int,
    file: UploadFile = File(...),
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.update_project_logo(project_id, file, current_user.id)