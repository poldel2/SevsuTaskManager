from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from models.domain.users import User
from repositories.user_repository import UserRepository
from core.config.settings import settings
from core.db import get_db

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=settings.SEVSU_AUTH_URL,
    tokenUrl=settings.SEVSU_TOKEN_URL
)

class NewUser:
    id: int

async def get_current_user():
#     token: str = Depends(oauth2_scheme),
#     session: AsyncSession = Depends(get_db)
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(
#             token,
#             settings.JWT_SECRET,
#             algorithms=[settings.JWT_ALGORITHM]
#         )
#         user_id: int = int(payload.get("sub"))
#         if user_id is None:
#             raise credentials_exception
#     except (JWTError, ValueError):
#         raise credentials_exception
#
#     user_repo = UserRepository(session)
#     user = await user_repo.get_by_id(user_id)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
      newUser = NewUser()
      newUser.id = 1
      return newUser


