from typing import Dict
from fastapi import WebSocket
from models.schemas.notifications import NotificationResponse

class NotificationManager:
    def __init__(self):
        self.websocket_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Подключение нового пользователя"""
        await websocket.accept()
        self.websocket_connections[user_id] = websocket

    async def disconnect(self, user_id: int = None):
        """Отключение пользователя или всех пользователей"""
        if user_id:
            if user_id in self.websocket_connections:
                try:
                    await self.websocket_connections[user_id].close()
                except:
                    pass
                del self.websocket_connections[user_id]
        else:
            for ws in self.websocket_connections.values():
                try:
                    await ws.close()
                except:
                    pass
            self.websocket_connections.clear()
            
    async def send_notification(self, user_id: int, notification: NotificationResponse):
        """Отправка уведомления через WebSocket"""
        if connection := self.websocket_connections.get(user_id):
            try:
                await connection.send_json({
                    "type": "notification",
                    "data": notification.model_dump()
                })
            except Exception:
                await self.disconnect(user_id)