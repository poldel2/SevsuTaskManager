from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.security import oauth2_scheme
from models.schemas.users import UserResponse, Token, UserCreate
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

    async def authenticate_user(self, code: str) -> Token:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_data = {
                "client_id": settings.SEVSU_CLIENT_ID,
                "client_secret": settings.SEVSU_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code"
            }

            token_response = await client.post(
                settings.SEVSU_TOKEN_URL,
                data=token_data
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization code"
                )

            access_token = token_response.json()["access_token"]

            # Get user info
            user_response = await client.get(
                settings.SEVSU_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            user_info = user_response.json()

        # Create/update user
        user = await self.user_repo.get_by_sub(user_info["sub"])
        if not user:
            user_data = UserCreate(
                sub=user_info["sub"],
                email=user_info["email"],
                first_name=user_info.get("given_name"),
                last_name=user_info.get("family_name"),
                middle_name=user_info.get("middle_name"),
                group=user_info.get("syncable_cohorts", [""])[0]
            )
            user = await self.user_repo.create_user(user_data)

        return self.create_jwt(user)

    def create_jwt(self, user: UserResponse) -> Token:
        payload = {
            "sub": str(user.id),
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        return Token(access_token=token, token_type="bearer")

    async def get_current_user(
        self,
        token: str = oauth2_scheme,
    ) -> UserResponse:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = int(payload["sub"])
        except (JWTError, ValueError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.model_validate(user)

    async def createUser(
            self,
            user: UserCreate
    ):
        await self.user_repo.create_user(user)
