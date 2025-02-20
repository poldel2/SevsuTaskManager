from fastapi import APIRouter, Depends, HTTPException, status
from services.task_service import TaskService
from models.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse
from core.security import get_current_user
from dependencies import get_task_service

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: int,
    task_data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.create_task(
        {**task_data.model_dump(), "project_id": project_id},
        current_user.id
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    project_id: int,
    task_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_task(task_id, current_user.id)

@router.get("/", response_model=list[TaskResponse])
async def get_tasks_by_project(
    project_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_tasks_by_project(project_id, current_user.id)

@router.get("/sprint/{sprint_id}", response_model=list[TaskResponse])
async def get_tasks_by_sprint(
    project_id: int,
    sprint_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_tasks_by_sprint(sprint_id, current_user.id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.update_task(task_id, task_data.model_dump(), current_user.id)

@router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.update_task_partial(task_id, task_data.model_dump(exclude_unset=True), current_user.id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    project_id: int,
    task_id: int,
    service: TaskService = Depends(get_task_service),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_task(task_id, current_user.id)
