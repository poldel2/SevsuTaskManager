from fastapi import APIRouter
from .auth import router as auth_router
from .projects import router as projects_router
from .sprints import router as sprints_router
from .task import router as task_router
from .chat import router as chat_router
from .notifications import router as notifications_router
from .report import router as reports_router
from .media import router as media_router
from .user import router as users_router

router = APIRouter()

router.include_router(auth_router, tags=["auth"])
router.include_router(projects_router,  tags=["projects"])
router.include_router(sprints_router, tags=["sprints"])
router.include_router(task_router, tags=["tasks"])
router.include_router(chat_router, tags=["chat"])
router.include_router(notifications_router, tags=["notifications"])
router.include_router(reports_router, tags=["reports"])
router.include_router(media_router, tags=["media"])
router.include_router(users_router, tags=["users"])
