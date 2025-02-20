from fastapi import APIRouter
from .auth import router as auth_router
from .projects import router as projects_router
from .sprints import router as sprints_router
from .task import router as task_router

router = APIRouter()

router.include_router(auth_router, tags=["auth"])
router.include_router(projects_router,  tags=["projects"])
router.include_router(sprints_router, tags=["sprints"])
router.include_router(task_router, tags=["tasks"])
