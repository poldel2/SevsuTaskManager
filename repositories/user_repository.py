import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from passlib.context import CryptContext
from typing import Optional, Sequence

from models.domain.users import User
from models.domain.tokens import Token
from models.schemas.users import UserCreate, UserResponse

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        hashed_password = self.pwd_context.hash(user_data.password) if user_data.password else None
        user = User(
            sub=user_data.sub,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            group=user_data.group,
            hashed_password=hashed_password
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserResponse.model_validate(user)

    async def get_by_sub(self, sub: str) -> Optional[UserResponse]:
        result = await self.session.execute(select(User).where(User.sub == sub))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def get_by_id(self, user_id: int) -> Optional[UserResponse]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        token_obj = Token(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        self.session.add(token_obj)
        await self.session.commit()

    async def get_token(self, token: str) -> Optional[Token]:
        result = await self.session.execute(select(Token).where(Token.token == token))
        return result.scalar_one_or_none()

    async def revoke_token(self, token: str) -> None:
        await self.session.execute(
            update(Token)
            .where(Token.token == token)
            .values(is_active=False)
        )
        await self.session.commit()

    async def search_users(self, query: str) -> Sequence[UserResponse]:
        search_pattern = f"%{query}%"
        stmt = select(User).where(
            (func.lower(User.first_name).like(func.lower(search_pattern))) |
            (func.lower(User.last_name).like(func.lower(search_pattern))) |
            (func.lower(User.email).like(func.lower(search_pattern)))
        )
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]

    async def update(self, user_id: int, data: dict) -> User:
        """Обновляет данные пользователя"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            await self.session.commit()
            await self.session.refresh(user)
        
        return user