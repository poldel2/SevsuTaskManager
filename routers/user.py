from fastapi import APIRouter, Depends, File, UploadFile
from core.security import get_current_user
from dependencies import get_user_service, get_project_service
from services.user_service import UserService
from models.schemas.users import UserResponse
from models.schemas.users import UserUpdate
from models.schemas.projects import ProjectCreate, ProjectUpdate, Project
from services.project_service import ProjectService


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.update_avatar(current_user.id, file)

@router.put("/profile")
async def update_profile(
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: UserResponse = Depends(get_current_user)
):
    return await service.update_profile(current_user.id, user_data)


@router.get("/{user_id}/projects", response_model=list[Project])
async def get_all_projects(
    user_id: int,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_all_public_projects(user_id)