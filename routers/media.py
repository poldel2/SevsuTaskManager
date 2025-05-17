from fastapi import APIRouter, Depends, Response
from dependencies import get_storage_service
from core.storage.service import StorageService

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/{file_path:path}")
async def get_media_file(
    file_path: str,
    storage_service: StorageService = Depends(get_storage_service)
):
    content, content_type = await storage_service.get_file(file_path)
    return Response(content=content, media_type=content_type)