from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl
import os
from core.config.settings import Settings as MainSettings

class TestSettings(BaseSettings):
    DATABASE_URL: str
    CALLBACK_URL: str
    SEVSU_CLIENT_ID: str
    SEVSU_CLIENT_SECRET: str
    SEVSU_AUTH_URL: str = "https://auth.sevsu.ru/realms/portal/protocol/openid-connect/auth"
    SEVSU_TOKEN_URL: str = "https://auth.sevsu.ru/realms/portal/protocol/openid-connect/token"
    SEVSU_USERINFO_URL: str = "https://auth.sevsu.ru/realms/portal/protocol/openid-connect/userinfo"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    TESTING: bool = True

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="forbid"
    )

    __test__ = False
    
    @classmethod
    def sync_with_main_settings(cls, main_settings: MainSettings):
        """
        Обновляет экземпляр основных настроек значениями из тестовых настроек.
        Это нужно для обеспечения того, чтобы все сервисы использовали тестовую БД.
        """
        for field, value in cls().model_dump().items():
            if hasattr(main_settings, field):
                setattr(main_settings, field, value)

test_settings = TestSettings() 