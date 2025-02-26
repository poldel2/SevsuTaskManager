from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.domain.messages import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, message_data: dict) -> Message:
        try:
            message = Message(**message_data)
            self.session.add(message)
            await self.session.commit()
            await self.session.refresh(message)
            return message
        except Exception as e:
            await self.session.rollback()
            raise

    async def get_by_id(self, message_id: int) -> Message | None:
        result = await self.session.execute(
            select(Message)
            .options(
                selectinload(Message.project),
                selectinload(Message.sender),
            )
            .where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_messages_by_project(self, project_id: int, limit: int = 50) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .options(
                selectinload(Message.project),
                selectinload(Message.sender),
            )
            .where(Message.project_id == project_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()