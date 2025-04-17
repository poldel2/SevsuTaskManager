from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_notification_manager, get_notification_service
from core.security import get_current_user, get_current_user_websocket
from models.domain.users import User
from models.schemas.notifications import NotificationResponse
from repositories.notification_repository import NotificationRepository
from services.notification_service import NotificationService
from services.notification_manager import NotificationManager

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Получить список уведомлений пользователя"""
    return await service.get_user_notifications(
        current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Отметить уведомление как прочитанное"""
    success = await service.mark_as_read(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success"}

@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Отметить все уведомления как прочитанные"""
    success = await service.mark_all_as_read(current_user.id)
    return {"status": "success"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Удалить уведомление"""
    success = await service.delete_notification(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"status": "success"}

@router.websocket("/ws")
async def websocket_notifications(
    websocket: WebSocket,
    manager: NotificationManager = Depends(get_notification_manager),
    current_user: User = Depends(get_current_user_websocket)
):
    """WebSocket соединение для уведомлений в реальном времени"""
    await manager.connect(websocket, current_user.id)
    try:
        await websocket.receive_text()
    except:
        await manager.disconnect(current_user.id)