from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import object_session
from models.domain.user_project import user_project_table

class UserCreate(BaseModel):
    sub: Optional[str] = None
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    group: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    sub: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    is_teacher: bool = False
    project_roles: dict[int, str] = {}

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        data = obj.__dict__.copy()
        
        data["is_teacher"] = getattr(obj, 'is_teacher', False)
        
        data["project_roles"] = {}
        
        try:

            
            session = object_session(obj)
            if session:
                role_records = session.query(
                    user_project_table.c.project_id,
                    user_project_table.c.role
                ).filter(
                    user_project_table.c.user_id == obj.id
                ).all()
                
                for project_id, role in role_records:
                    if hasattr(role, 'value'):
                        data["project_roles"][project_id] = role.value
        except Exception:
            pass
        
        return cls(**data)

class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str