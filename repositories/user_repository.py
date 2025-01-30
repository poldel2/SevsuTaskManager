from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.domain.users import User
from models.schemas.users import UserCreate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_sub(self, sub: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.sub == sub)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user