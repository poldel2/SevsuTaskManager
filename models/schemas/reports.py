from datetime import datetime, date
from typing import Dict, Any

from pydantic import BaseModel, Json
from sqlalchemy.dialects.postgresql import JSONB


class ReportBase(BaseModel):
    title: str
    period_start: date
    period_end: date
    data: Dict[str, Any]

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}