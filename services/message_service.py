import logging
from fastapi import HTTPException, status, WebSocket, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.domain.messages import Message
from repositories.message_repository import MessageRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository
from models.schemas.messages import MessageCreate, MessageResponse
from core.db import get_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MessageService, cls).__new__(cls)
            cls._instance.websocket_connections = {}
        return cls._instance

    def __init__(
        self,
        message_repository: MessageRepository = Depends(),
        project_repository: ProjectRepository = Depends(),
        user_repository: UserRepository = Depends(),
    ):
        if not hasattr(self, 'initialized'):
            self.message_repository = message_repository
            self.project_repository = project_repository
            self.user_repository = user_repository
            self.initialized = True

    async def _validate_project_access(self, project_id: int, user_id: int | None):
        if user_id is None:
            logger.warning(f"Пропущена проверка доступа для project_id={project_id}")
            return
        project = await self.project_repository.get_by_id(project_id)
        project_users = await self.project_repository.get_project_users(project_id)
        logger.info(f"project_users={project_users}")
        if not project or not any(user.id == user_id for user in project_users):
            logger.error(f"Нет доступа к проекту {project_id} для user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to project"
            )
        logger.info(f"Доступ к проекту {project_id} подтвержден для user_id={user_id}")

    async def create_message(self, project_id: int, message_data: MessageCreate, user_id: int | None) -> MessageResponse:
        await self._validate_project_access(project_id, user_id)

        message = await self.message_repository.create({
            "project_id": project_id,
            "sender_id": user_id if user_id else 0,
            "content": message_data.content,
        })
        logger.info(f"Создано сообщение id={message.id} для project_id={project_id}")

        query = await self.message_repository.session.execute(
            select(Message)
            .options(
                selectinload(Message.project),
                selectinload(Message.sender),
            )
            .filter_by(id=message.id)
        )
        message = query.scalar_one()

        response = MessageResponse.model_validate({
            **message.__dict__,
            "sender_name": message.sender.last_name if message.sender else "Anonymous",
        })
        logger.info(f"Подготовлено сообщение для рассылки: {response}")

        await self.broadcast_message(project_id, response)
        return response

    async def get_messages_by_project(self, project_id: int, user_id: int | None) -> list[MessageResponse]:
        await self._validate_project_access(project_id, user_id)
        messages = await self.message_repository.get_messages_by_project(project_id)
        logger.info(f"Получено {len(messages)} сообщений для project_id={project_id}")
        return [
            MessageResponse.model_validate({
                **message.__dict__,
                "sender_name": message.sender.last_name if message.sender else "Anonymous",
            })
            for message in messages
        ]

    async def connect(self, websocket: WebSocket, project_id: int, user_id: int | None):
        await self._validate_project_access(project_id, user_id)
        await websocket.accept()
        if project_id not in self.websocket_connections:
            self.websocket_connections[project_id] = []
        if websocket not in self.websocket_connections[project_id]:
            self.websocket_connections[project_id].append(websocket)
        logger.info(f"Клиент подключен к project_id={project_id}. Всего соединений: {len(self.websocket_connections[project_id])}")

    async def disconnect(self, websocket: WebSocket, project_id: int):
        if project_id in self.websocket_connections and websocket in self.websocket_connections[project_id]:
            self.websocket_connections[project_id].remove(websocket)
            logger.info(f"Клиент отключен от project_id={project_id}. Осталось соединений: {len(self.websocket_connections[project_id])}")
            if not self.websocket_connections[project_id]:
                del self.websocket_connections[project_id]
                logger.info(f"Все клиенты отключены от project_id={project_id}")

    async def broadcast_message(self, project_id: int, message: MessageResponse):
        if project_id not in self.websocket_connections:
            logger.warning(f"Нет активных соединений для project_id={project_id}")
            return

        logger.info(f"Рассылка сообщения для {len(self.websocket_connections[project_id])} клиентов в project_id={project_id}")
        message_data = {
            "id": message.id,
            "project_id": message.project_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "sender_name": message.sender_name,
        }
        disconnected_clients = []
        for websocket in self.websocket_connections[project_id][:]:
            try:
                await websocket.send_json(message_data)
                logger.info(f"Сообщение отправлено клиенту в project_id={project_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки клиенту в project_id={project_id}: {e}")
                disconnected_clients.append(websocket)

        for websocket in disconnected_clients:
            await self.disconnect(websocket, project_id)