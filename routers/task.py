from fastapi import APIRouter, Depends, HTTPException, status

from models.domain.tasks import TaskStatus, TaskGrade
from models.domain.users import User
from services.task_service import TaskService
from models.schemas.tasks import TaskCreate, TaskUpdate, TaskResponse, TaskApproval, TaskRejection
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


@router.post("/{task_id}/submit-for-review", response_model=TaskResponse)
async def submit_for_review(
        project_id: int,
        task_id: int,
        service: TaskService = Depends(get_task_service),
        current_user: dict = Depends(get_current_user)
):
    """Отправка задачи на проверку"""
    return await service.update_task_partial(
        task_id,
        {"status": TaskStatus.NEED_REVIEW.value},
        current_user.id
    )


@router.post("/{task_id}/approve")
async def approve_task(
        task_id: int,
        approval_data: TaskApproval,
        service: TaskService = Depends(get_task_service),
        current_user: User = Depends(get_current_user)  # Убедитесь что возвращает User модель
):
    task = await service.get_task(task_id, current_user.id)

    if approval_data.is_teacher_approval:
        if not current_user.is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can perform teacher approval"
            )
        if task.grade != TaskGrade.HARD:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only hard tasks require teacher approval"
            )
    else:
        if not await service._is_project_leader(current_user.id, task.project_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project leaders can approve tasks"
            )

    new_status = TaskStatus.APPROVED_BY_TEACHER if approval_data.is_teacher_approval else TaskStatus.APPROVED_BY_LEADER
    return await service.update_task_partial(
        task_id,
        {"status": new_status.value},
        current_user.id
    )


@router.post("/{task_id}/reject", response_model=TaskResponse)
async def reject_task(
        task_id: int,
        rejection_data: TaskRejection,
        service: TaskService = Depends(get_task_service),
        current_user: dict = Depends(get_current_user)
):
    """Отклонение задачи с комментарием"""
    return await service.update_task_partial(
        task_id,
        {
            "status": TaskStatus.REJECTED.value,
            "feedback": rejection_data.feedback
        },
        current_user.id
    )


@router.patch("/{task_id}")
async def patch_task(
        task_id: int,
        task_data: TaskUpdate,
        service: TaskService = Depends(get_task_service),
        current_user: User = Depends(get_current_user)
):
    task = await service.get_task(task_id, current_user.id)

    can_edit = (
            current_user.is_teacher or
            task.assignee_id == current_user.id or
            await service._is_project_leader(current_user.id, task.project_id)
    )

    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to edit this task"
        )

    return await service.update_task_partial(
        task_id,
        task_data.model_dump(exclude_unset=True),
        current_user.id
    )

