from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
import os

class Settings(BaseSettings):
    DATABASE_URL: str
    CALLBACK_URL: str
    SEVSU_CLIENT_ID: str
    SEVSU_CLIENT_SECRET: str
    SEVSU_AUTH_URL: str = "https://auth.sevsu.ru/realms/portal/protocol/openid-connect/auth"
    SEVSU_TOKEN_URL: str = "https://auth.sevsu.ru/realms/portal/protocol/openid-connect/token"
    SEVSU_USERINFO_URL: str = "https://auth.sevsu.ru/realms/portal/protocol/openid-connect/userinfo"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000
    MINIO_USE_SSL: bool = False
    MINIO_BUCKET_NAME: str = "tasktracker"
    MINIO_PUBLIC_HOST: str = "localhost"
    MINIO_BUCKET: str = "media"

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("TESTING") else ".env",
        env_file_encoding="utf-8",
        extra="forbid"
    )

settings = Settings()