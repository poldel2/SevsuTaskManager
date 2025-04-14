from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    project_id: int
    sender_id: int
    content: str
    created_at: datetime
    sender_name: Optional[str] = None

    model_config = {"from_attributes": True}