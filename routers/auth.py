from fastapi import APIRouter, Depends, Request
from starlette import status

from dependencies import get_auth_service
from services.auth_service import AuthService
from models.schemas.users import Token, UserResponse, UserCreate, UserLogin
from core.config.settings import settings
from core.security import get_current_user, oauth2_scheme  # Импортируем из security

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
    return await auth_service.authenticate_user_sevsu(code)

@router.post("/login/local", response_model=Token)
async def login_local(
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.authenticate_user_local(user_login.email, user_login.password)

@router.get("/me", response_model=UserResponse)
async def get_current_user_route(
    current_user: UserResponse = Depends(get_current_user)  # Используем зависимость из security
):
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.create_user(user)

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.revoke_token(token)
    return {"message": "Logged out successfully"}