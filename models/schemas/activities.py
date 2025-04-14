from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from models.schemas.users import UserResponse

class ActivityResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    entity_type: str
    entity_id: int
    action: str
    changes: Optional[Dict[str, Any]]
    created_at: datetime
    user: Optional[UserResponse] = None
    formatted_message: Optional[str] = None
    
    model_config = {"from_attributes": True}