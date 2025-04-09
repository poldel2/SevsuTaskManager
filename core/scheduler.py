from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dependencies import get_db
from services.notification_service import NotificationService
from repositories.notification_repository import NotificationRepository
import logging

logger = logging.getLogger(__name__)

async def cleanup_notifications():
    """Периодическая задача очистки старых уведомлений"""
    try:
        async for db in get_db():
            service = NotificationService(NotificationRepository(db))
            deleted_count = await service.cleanup_old_notifications()
            logger.info(f"Удалено {deleted_count} старых уведомлений")
    except Exception as e:
        logger.error(f"Ошибка при очистке уведомлений: {e}")

def setup_scheduler():
    """Настройка планировщика задач"""
    scheduler = AsyncIOScheduler()
    
    # Запуск очистки уведомлений каждый день в 03:00
    scheduler.add_job(
        cleanup_notifications,
        CronTrigger(hour=3, minute=0),
        id="cleanup_notifications",
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler