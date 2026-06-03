from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )


class RedisConfig(AppBaseSettings):
    host: str = "localhost"
    port: int = 6379
    db_cache: int = 0
    echo: bool = False

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
    )

    @property
    def get_redis_URL(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db_cache}"


class DatabaseConfig(AppBaseSettings):
    name: str = ""
    user: str = ""
    password: str = ""
    port: int = 5432
    host: str = "localhost"
    echo: bool = False

    model_config = SettingsConfigDict(
        env_prefix="PG_",
    )

    @property
    def get_database_URL(self) -> str:
        return f"postgresql+psycopg_async://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class DjangoConfig(AppBaseSettings):
    api_url: str = "http://django:8000/api/pages/"
    internal_secret_key: str = "internal_secret_key"

    model_config = SettingsConfigDict(
        env_prefix="DJANGO_",
    )


class Settings(AppBaseSettings):
    JWT_SECRET_KEY: str = "jwt_secret_key"
    JWT_REFRESH_SECRET_KEY: str = "jwt_refresh_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    redis: RedisConfig = Field(default_factory=RedisConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    django: DjangoConfig = Field(default_factory=DjangoConfig)


settings = Settings()
