from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.security import oauth2_scheme
from models.schemas.users import UserResponse, Token, UserCreate, UserLogin
from repositories.user_repository import UserRepository
from core.config.settings import settings
import httpx

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=settings.SEVSU_AUTH_URL,
            tokenUrl=settings.SEVSU_TOKEN_URL
        )
        self.local_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/local")

    async def authenticate_user_sevsu(self, code: str) -> Token:
        async with httpx.AsyncClient() as client:
            token_data = {
                "client_id": settings.SEVSU_CLIENT_ID,
                "client_secret": settings.SEVSU_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code"
            }
            token_response = await client.post(settings.SEVSU_TOKEN_URL, data=token_data)
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization code"
                )
            access_token = token_response.json()["access_token"]
            user_response = await client.get(
                settings.SEVSU_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = user_response.json()

        user = await self.user_repo.get_by_sub(user_info["sub"])
        if not user:
            user_data = UserCreate(
                sub=user_info["sub"],
                email=user_info["email"],
                first_name=user_info.get("given_name"),
                last_name=user_info.get("family_name"),
                middle_name=user_info.get("middle_name"),
                group=user_info.get("syncable_cohorts", [""])[0],
                password=None
            )
            user = await self.user_repo.create_user(user_data)

        return await self.create_jwt(user)

    async def authenticate_user_local(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.hashed_password or not self.user_repo.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return await self.create_jwt(user)

    async def create_jwt(self, user) -> Token:
        """
        Создает JWT токен для пользователя.
        Параметр user может быть как объектом User, так и UserResponse
        """
        user_id = user.id
        
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        payload = {
            "sub": str(user_id),
            "exp": expires_at
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        await self.user_repo.create_token(user_id, token, expires_at)
        return Token(access_token=token, token_type="bearer")

    async def create_user(self, user: UserCreate) -> UserResponse:
        if await self.user_repo.get_by_email(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        return await self.user_repo.create_user(user)

    async def revoke_token(self, token: str) -> None:
        await self.user_repo.revoke_token(token)

    async def get_current_user_info(self, user_id: int) -> UserResponse:
        """
        Получить информацию о текущем пользователе для фронтенда
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_response = UserResponse.model_validate(user)
        return user_response