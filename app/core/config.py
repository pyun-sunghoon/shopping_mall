from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 서비스 역할 키는 서버에서만 사용한다.
    supabase_url: str
    supabase_service_role_key: SecretStr
    secret_key: SecretStr = Field(min_length=32)
    cookie_secure: bool = False
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
