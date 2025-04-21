from repositories.activity_repository import ActivityRepository
from typing import Dict, Any, List
from enum import Enum
from repositories.user_repository import UserRepository
from models.schemas.activities import ActivityResponse
from repositories.task_column_repository import TaskColumnRepository
from datetime import datetime

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
    def __init__(
        self, 
        activity_repository: ActivityRepository,
        user_repository: UserRepository,
        column_repository: TaskColumnRepository
    ):
        self.repository = activity_repository
        self.user_repository = user_repository
        self.column_repository = column_repository
    
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
        offset: int = 0,
        start_date: datetime = None,
        end_date: datetime = None,
        action: str = None
    ):
        activities = await self.repository.get_project_activities(
            project_id=project_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            action=action
        )
        
        total = await self.repository.count_project_activities(
            project_id=project_id,
            start_date=start_date,
            end_date=end_date,
            action=action
        )
        
        formatted_activities = []
        for activity in activities:
            user = await self.user_repository.get_by_id(activity.user_id)
            activity_dict = vars(activity)
            activity_dict['user'] = user
            
            formatted_message = await self._format_activity_message(activity)
            activity_dict['formatted_message'] = formatted_message
            
            formatted_activities.append(ActivityResponse(**activity_dict))
            
        return {"items": formatted_activities, "total": total}

    async def _format_activity_message(self, activity) -> str:
        """Форматирует сообщение об активности в человекочитаемый вид"""
        if not activity.changes:
            return f"{activity.action.lower()} {activity.entity_type.lower()}"
            
        if activity.entity_type == EntityType.TASK:
            return await self._format_task_changes(activity)
            
        return f"{activity.action.lower()} {activity.entity_type.lower()}"

    async def _format_task_changes(self, activity) -> str:
        """Форматирует изменения задачи"""
        changes = activity.changes
        old_data = changes.get("old", {})
        new_data = changes.get("new", {})
        changed_fields = changes.get("changed_fields", {})

        messages = []
        task_title = new_data.get('title', '')
        
        if "title" in changed_fields:
            messages.append(f"изменил название задачи с '{old_data.get('title')}' на '{new_data.get('title')}'")
            task_title = new_data.get('title')
            
        if "column_id" in changed_fields:
            old_column = await self.column_repository.get_by_id(old_data.get("column_id"))
            new_column = await self.column_repository.get_by_id(new_data.get("column_id"))
            status_msg = "изменил статус задачи"
            if not messages: 
                status_msg = f"{status_msg} '{task_title}'"
            messages.append(f"{status_msg} с '{old_column.name if old_column else 'нет'}' на '{new_column.name if new_column else 'нет'}'")
            
        if "priority" in changed_fields:
            priority_names = {
                "high": "высокий",
                "medium": "средний", 
                "low": "низкий"
            }
            old_priority = priority_names.get(old_data.get('priority', '').lower(), old_data.get('priority', ''))
            new_priority = priority_names.get(new_data.get('priority', '').lower(), new_data.get('priority', ''))
            
            priority_msg = "изменил приоритет задачи"
            if not messages: 
                priority_msg = f"{priority_msg} '{task_title}'"
            messages.append(f"{priority_msg} с '{old_priority}' на '{new_priority}'")
            
        if not messages:
            return f"{activity.action.lower()} задачу '{task_title}'"
            
        return ", ".join(messages)