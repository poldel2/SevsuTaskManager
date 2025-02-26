from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from services.message_service import MessageService
from models.schemas.messages import MessageCreate, MessageResponse
from core.security import get_current_user
from dependencies import get_message_service

router = APIRouter(prefix="/projects/{project_id}/chat", tags=["chat"])

@router.post("/messages/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    project_id: int,
    message_data: MessageCreate,
    service: MessageService = Depends(get_message_service),
    current_user: dict = Depends(get_current_user),
):
    return await service.create_message(project_id, message_data, current_user.id)

@router.get("/messages/", response_model=list[MessageResponse])
async def get_messages(
    project_id: int,
    service: MessageService = Depends(get_message_service),
    current_user: dict = Depends(get_current_user),
):
    return await service.get_messages_by_project(project_id, current_user.id)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: int,
    service: MessageService = Depends(get_message_service),
    current_user: dict = Depends(get_current_user),
):
    await service.connect(websocket, project_id, current_user.id)
    try:
        while True:
            data = await websocket.receive_text()  # Получаем текст от клиента
            message_data = MessageCreate(content=data)  # Создаем объект сообщения
            await service.create_message(project_id, message_data, current_user.id)  # Сохраняем и рассылаем
    except WebSocketDisconnect:
        await service.disconnect(websocket, project_id)