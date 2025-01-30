from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    sub: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    group: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    sub: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str