from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas.sprints import SprintCreate, SprintUpdate, SprintResponse
from services.sprint_service import SprintService
from core.db import get_db
from core.security import get_current_user
from dependencies import get_sprint_service

router = APIRouter(prefix="/projects/{project_id}/sprints", tags=["sprints"])

@router.post("/", response_model=SprintResponse, status_code=status.HTTP_201_CREATED)
async def create_sprint(
    project_id: int,
    sprint_data: SprintCreate,
    service: SprintService = Depends(get_sprint_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.create_sprint(
        {**sprint_data.model_dump(), "project_id": project_id},
        current_user.id
    )

@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    project_id: int,
    sprint_id: int,
    service: SprintService = Depends(get_sprint_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_sprint(sprint_id, current_user.id)

@router.get("/", response_model=list[SprintResponse])
async def get_all_sprints(
    project_id: int,
    service: SprintService = Depends(get_sprint_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_project_sprints(project_id, current_user.id)

@router.put("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    project_id: int,
    sprint_id: int,
    sprint_data: SprintUpdate,
    service: SprintService = Depends(get_sprint_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.update_sprint(sprint_id, sprint_data.model_dump(), current_user.id)

@router.delete("/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    project_id: int,
    sprint_id: int,
    service: SprintService = Depends(get_sprint_service),
    current_user: dict = Depends(get_current_user)
):
    await service.delete_sprint(sprint_id, current_user.id)