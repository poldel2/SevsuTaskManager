from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid"
    )

settings = Settings()