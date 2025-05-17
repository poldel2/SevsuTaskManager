from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException, status
from typing import Optional, BinaryIO
from core.config.settings import settings
import os
from io import BytesIO

class StorageService:
    def __init__(self):
        self.client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Проверяет существование bucket и создает его если нужно"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize storage: {str(e)}"
            )

    def _get_project_path(self, project_id: int) -> str:
        """Формирует путь для хранения файлов проекта"""
        return f"project_{project_id}"

    async def upload_file(self, entity_id: int, file: BinaryIO, filename: str, is_user: bool = False) -> str:
        """Загружает файл в хранилище"""
        try:
            # Формируем путь для сохранения
            prefix = f"user_{entity_id}" if is_user else f"project_{entity_id}"
            object_name = f"{prefix}/{filename}"

            file_content = file.read()
            file_size = len(file_content)
            file_bytes = BytesIO(file_content)
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_bytes,
                length=file_size,
                content_type=getattr(file, 'content_type', 'application/octet-stream')
            )
            
            # Возвращаем относительный путь
            return f"/media/{object_name}"
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )

    async def delete_file(self, project_id: int, filename: str):
        """Удаляет файл из хранилища"""
        try:
            file_path = f"{self._get_project_path(project_id)}/{filename}"
            self.client.remove_object(self.bucket_name, file_path)
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )

    async def delete_project_files(self, project_id: int):
        """Удаляет все файлы проекта"""
        try:
            project_path = self._get_project_path(project_id)
            objects = self.client.list_objects(self.bucket_name, prefix=project_path)
            for obj in objects:
                self.client.remove_object(self.bucket_name, obj.object_name)
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete project files: {str(e)}"
            )

    async def get_file(self, file_path: str) -> tuple[bytes, str]:
        """Получает файл из хранилища"""
        try:
            response = self.client.get_object(self.bucket_name, file_path)
            return response.read(), response.headers.get('content-type', 'application/octet-stream')
        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )