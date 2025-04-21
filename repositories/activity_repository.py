from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.domain.project_activities import ProjectActivity
from typing import List, Optional, Dict, Any

def serialize_datetime(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime(item) for item in obj]
    return obj

class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, 
        project_id: int,
        user_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        changes: dict = None
    ) -> ProjectActivity:
        activity = ProjectActivity(
            project_id=project_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changes=serialize_datetime(changes) if changes else None
        )
        self.session.add(activity)
        await self.session.commit()
        return activity

    async def get_project_activities(
        self,
        project_id: int,
        limit: int = 50,
        offset: int = 0,
        start_date: datetime = None,
        end_date: datetime = None,
        action: str = None
    ) -> List[ProjectActivity]:
        query = select(ProjectActivity).where(ProjectActivity.project_id == project_id)

        if start_date and end_date:
            query = query.where(and_(
                ProjectActivity.created_at >= start_date,
                ProjectActivity.created_at <= end_date
            ))

        if action:
            query = query.where(ProjectActivity.action == action)

        query = query.order_by(ProjectActivity.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_project_activities(
        self,
        project_id: int,
        start_date: datetime = None,
        end_date: datetime = None,
        action: str = None
    ) -> int:
        conditions = [ProjectActivity.project_id == project_id]

        if start_date and end_date:
            conditions.append(and_(
                ProjectActivity.created_at >= start_date,
                ProjectActivity.created_at <= end_date
            ))

        if action:
            conditions.append(ProjectActivity.action == action)

        result = await self.session.execute(
            select(func.count()).select_from(ProjectActivity).where(and_(*conditions))
        )
        return result.scalar_one()