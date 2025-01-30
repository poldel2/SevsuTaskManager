from fastapi import APIRouter, Depends, Request

from dependencies import get_auth_service
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas.users import Token, UserResponse, UserCreate
from core.db import get_db
from core.config.settings import settings

router = APIRouter(tags=["Authentication"])


@router.get("/login/sevsu")
async def login_via_sevsu():
    return {
        "auth_url": (
            f"{settings.SEVSU_AUTH_URL}?"
            f"response_type=code&"
            f"client_id={settings.SEVSU_CLIENT_ID}&"
            f"redirect_uri={settings.CALLBACK_URL}"
        )
    }

@router.get("/callback", response_model=Token)
async def auth_callback(
    code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.authenticate_user(code)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: UserResponse = Depends(AuthService.get_current_user)
):
    return current_user

@router.post("/newUser")
async def newUser(
        user: UserCreate,
        auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.createUser(user)
