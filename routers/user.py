from fastapi import APIRouter, Depends, File, UploadFile
from core.security import get_current_user
from dependencies import get_user_service
from services.user_service import UserService
from models.schemas.users import UserResponse
from models.schemas.users import UserUpdate

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