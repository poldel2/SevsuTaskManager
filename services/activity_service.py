from repositories.activity_repository import ActivityRepository
from typing import Dict, Any, List
from enum import Enum

class EntityType(str, Enum):
    TASK = "TASK"
    SPRINT = "SPRINT"
    COLUMN = "COLUMN"
    PROJECT = "PROJECT"

class ActionType(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class ActivityService:
    def __init__(self, activity_repository: ActivityRepository):
        self.repository = activity_repository
    
    async def log_activity(
        self,
        project_id: int,
        user_id: int,
        entity_type: EntityType,
        entity_id: int,
        action: ActionType,
        changes: Dict[str, Any] = None
    ):
        await self.repository.create(
            project_id=project_id,
            user_id=user_id,
            entity_type=entity_type.value,
            entity_id=entity_id,
            action=action.value,
            changes=changes
        )

    async def get_project_activities(
        self,
        project_id: int,
        limit: int = 50,
        offset: int = 0
    ):
        return await self.repository.get_project_activities(
            project_id=project_id,
            limit=limit,
            offset=offset
        )