from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile
from io import BytesIO

from models.domain.projects import Project
from models.schemas.projects import ProjectCreate, ProjectUpdate
from models.schemas.users import UserResponse
from repositories.project_repository import ProjectRepository
from repositories.task_column_repository import TaskColumnRepository
from repositories.user_repository import UserRepository
from models.domain.users import User
from models.domain.user_project import Role
from services.notification_service import NotificationService
from core.storage.service import StorageService
from core.storage.utils import validate_file_type, validate_file_size, get_safe_filename


class ProjectService:
    def __init__(
        self,
        project_repository: ProjectRepository,
        notification_service: NotificationService,
        column_repository: TaskColumnRepository,
        storage_service: StorageService,
        user_repo: UserRepository  
    ):
        self.project_repo = project_repository
        self.notification_service = notification_service
        self.column_repo = column_repository
        self.storage_service = storage_service
        self.user_repo = user_repo

    async def validate_project_access(self, project_id: int, user_id: int):
        project = await self.project_repo.get_by_id(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to project"
            )

    async def create_project(self, project_data: dict, owner_id: int) -> Project:
        project = await self.project_repo.create({
            **project_data,
            "owner_id": owner_id
        })
        default_columns = [
            {"name": "К выполнению", "project_id": project.id, "position": 0, "color": "#b3b3b3"},
            {"name": "Выполнить", "project_id": project.id, "position": 1, "color": "#fabd06"},
            {"name": "Готово", "project_id": project.id, "position": 2, "color": "#22b622"},
        ]
        for column_data in default_columns:
            await self.column_repo.create(column_data)

        await self.project_repo.add_user_to_project(project.id, owner_id, "OWNER")
        return project

    async def get_user_projects(self, user_id: int) -> Sequence[Project]:
        projects = await self.project_repo.get_all_for_user(user_id)
        if not projects:
            return []
        return projects

    async def get_project(self, project_id: int, user_id: int) -> Optional[Project]:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        # Проверяем, является ли пользователь участником проекта
        user_ids = [u.id for u in project.users]
        if user_id not in user_ids and project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this project"
            )
        return project

    async def get_all_projects(self, user_id: int) -> Sequence[Project]:
        return await self.project_repo.get_all_for_user(user_id)

    async def get_all_public_projects(self, user_id: int) -> Sequence[Project]:
        projects = await self.get_all_projects(user_id)
        return [project for project in projects if not project.is_private]

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdate,
        user_id: int
    ) -> Project:
        project = await self.get_project(project_id, user_id)
        # Только владелец может обновлять проект
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update it"
            )
        return await self.project_repo.update(project_id, project_data.model_dump(exclude_unset=True))

    async def delete_project(self, project_id: int, user_id: int) -> None:
        project = await self.get_project(project_id, user_id)
        # Только владелец может удалять проект
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can delete it"
            )
        await self.project_repo.delete(project_id)

    async def add_user_to_project(
        self,
        project_id: int,
        user_id: int,
        role: str,
        inviter_id: int
    ) -> Project:
        user = await self.user_repo.get_by_id(user_id)
        
        if user and user.role == "teacher":
            role = "TEACHER"
            
        project = await self.project_repo.add_user_to_project(project_id, user_id, role)
        
        if project:
            inviter = await self.project_repo.get_user(inviter_id)
            await self.notification_service.notify_team_invitation(
                user_id=user_id,
                project_id=project.id,
                project_name=project.name,
                inviter_id=inviter_id,
                inviter_name=f"{inviter.first_name} {inviter.last_name}"
            )
        
        return project

    async def remove_user_from_project(self, project_id: int, user_id: int, current_user_id: int) -> None:
        project = await self.get_project(project_id, current_user_id)
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can remove users"
            )
        if user_id == project.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove project owner"
            )
        await self.project_repo.remove_user_from_project(project_id, user_id)

    async def get_project_users(self, project_id: int, user_id: int) -> Sequence[UserResponse]:
        await self.get_project(project_id, user_id)  # Проверка доступа
        return await self.project_repo.get_project_users(project_id)

    async def _is_user_project_leader(self, user_id: int, project_id: int) -> bool:
        """
        Check if user is project leader (owner or admin)
        """
        user = await self.project_repo.session.get(User, user_id)
        if not user:
            return False
        
        # Check if user is project owner
        project = await self.project_repo.get_by_id(project_id)
        if project and project.owner_id == user_id:
            return True
            
        # Check if user is project admin
        return user.is_project_leader(project_id)

    async def update_project_logo(self, project_id: int, file: UploadFile, user_id: int) -> Project:
        """Обновляет логотип проекта"""
        await self.validate_project_access(project_id, user_id)
        
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
        # Создаем новый BytesIO с прочитанными данными
        file_obj = BytesIO(contents)
        file_obj.content_type = file.content_type
        
        logo_url = await self.storage_service.upload_file(project_id, file_obj, safe_filename)
        return await self.project_repo.update(project_id, {"logo": logo_url})