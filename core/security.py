from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket

from core.db import get_db
from core.config.settings import settings
from repositories.user_repository import UserRepository
from models.schemas.users import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/local")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception

    user_repo = UserRepository(session)
    token_db = await user_repo.get_token(token)
    if not token_db or not token_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or revoked",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.model_validate(user)


async def get_current_user_websocket(
        websocket: WebSocket,
        session: AsyncSession = Depends(get_db)
) -> UserResponse:
    # Извлекаем токен из query-параметров
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        if user_id is None:
            await websocket.close(code=1008, reason="Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
    except (JWTError, ValueError):
        await websocket.close(code=1008, reason="Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    user_repo = UserRepository(session)
    token_db = await user_repo.get_token(token)
    if not token_db or not token_db.is_active:
        await websocket.close(code=1008, reason="Token is invalid or revoked")
        raise HTTPException(status_code=401, detail="Token is invalid or revoked")

    user = await user_repo.get_by_id(user_id)
    if user is None:
        await websocket.close(code=1008, reason="User not found")
        raise HTTPException(status_code=404, detail="User not found")

    # Используем model_validate для безопасного преобразования
    return UserResponse.model_validate(user)