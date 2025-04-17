from sqlalchemy import select, update, and_, delete, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from models.domain.notifications import Notification
from models.schemas.notifications import NotificationCreate, NotificationUpdate
from typing import List, Optional

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: NotificationCreate) -> Notification:
        db_notification = Notification(**notification.model_dump())
        self.session.add(db_notification)
        await self.session.commit()
        await self.session.refresh(db_notification)
        return db_notification

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.read == False)
            
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            update(Notification)
            .where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
            .values(read=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def mark_all_as_read(self, user_id: int) -> bool:
        result = await self.session.execute(
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.read == False
                )
            )
            .values(read=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete(self, notification_id: int, user_id: int) -> bool:
        notification = await self.get_by_id(notification_id)
        if notification and notification.user_id == user_id:
            await self.session.delete(notification)
            await self.session.commit()
            return True
        return False

    async def cleanup_old_notifications(self) -> int:
        """Удаляет старые уведомления:
        - Непрочитанные старше 30 дней
        - Прочитанные старше 7 дней после прочтения
        """
        current_time = datetime.utcnow()
        unread_threshold = current_time - timedelta(days=30)
        read_threshold = current_time - timedelta(days=7)

        result = await self.session.execute(
            delete(Notification).where(
                or_(
                    and_(
                        Notification.read == False,
                        Notification.created_at <= unread_threshold
                    ),
                    and_(
                        Notification.read == True,
                        Notification.created_at <= read_threshold
                    )
                )
            )
        )
        await self.session.commit()
        return result.rowcount