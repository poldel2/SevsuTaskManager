from typing import Sequence
from fastapi import HTTPException, status, UploadFile
from repositories.user_repository import UserRepository
from models.domain.users import User
from models.schemas.users import UserResponse, UserUpdate
from core.storage.utils import validate_file_type, validate_file_size, get_safe_filename
from core.storage.service import StorageService
from io import BytesIO

class UserService:
    def __init__(self, user_repository: UserRepository, storage_service: StorageService):
        self.user_repo = user_repository
        self.storage_service = storage_service

    async def search_users(self, query: str) -> Sequence[UserResponse]:
        return await self.repository.search_users(query)

    async def update_avatar(self, user_id: int, file: UploadFile) -> User:
        """Обновляет аватар пользователя"""
        contents = await file.read()
        if not validate_file_type(contents):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only images are allowed."
            )
        
        if not validate_file_size(len(contents)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 5MB."
            )

        safe_filename = get_safe_filename(file.filename)
        file_obj = BytesIO(contents)
        file_obj.content_type = file.content_type
        
        avatar_url = await self.storage_service.upload_file(user_id, file_obj, safe_filename, is_user=True)
        return await self.user_repo.update(user_id, {"avatar": avatar_url})

    async def update_profile(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновляет данные пользователя"""
        return await self.user_repo.update(user_id, user_data.model_dump(exclude_unset=True))