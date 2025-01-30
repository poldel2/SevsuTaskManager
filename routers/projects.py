from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.domain.users import User
from models.schemas.projects import ProjectCreate, ProjectUpdate, Project
from dependencies import get_project_service
from core.security import get_current_user
from services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project)
async def create_project(
        project_data: ProjectCreate,
        service: ProjectService = Depends(get_project_service),
        current_user: dict = Depends(get_current_user)
):
    project_data_dict = project_data.model_dump()
    return await service.create_project(project_data_dict, 1)  #TODO:: заменить на current_user.id


@router.get("/{project_id}", response_model=Project)
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
        current_user: dict = Depends(get_current_user)
):
    return await service.get_project(project_id, 1)  #TODO:: заменить на current_user.id


@router.get("/", response_model=list[Project])
async def get_all_projects(
        service: ProjectService = Depends(get_project_service),
        current_user: dict = Depends(get_current_user)
):
    return await service.get_all_projects(1)  #TODO:: заменить на current_user.id


@router.put("/{project_id}", response_model=Project)
async def update_project(
        project_id: int,
        project_data: ProjectUpdate,
        service: ProjectService = Depends(get_project_service),
        current_user: dict = Depends(get_current_user)
):
    return await service.update_project(project_id, project_data, 1)  #TODO:: заменить на current_user.id


@router.delete("/{project_id}")
async def delete_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
        current_user: dict = Depends(get_current_user)
):
    await service.delete_project(project_id, 1)  #TODO:: заменить на current_user.id
    return {"message": "Project deleted"}


@router.get("/{project_id}", response_model=Project)
async def get_project(
        project_id: int,
        service: ProjectService = Depends(get_project_service),
        current_user: User = Depends(get_current_user)
):
    project = await service.repository.get_by_id(project_id)

    if not project or project.owner_id != 1:  #TODO:: заменить на current_user.id
        raise HTTPException(status_code=404, detail="Project not found")

    return project
