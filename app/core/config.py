from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class RedisConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db_cache: int = 0
    echo: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="REDIS_",
        extra="ignore",
    )

    @property
    def get_redis_URL(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db_cache}"


class DatabaseConfig(BaseSettings):
    name: str = ""
    user: str = ""
    password: str = ""
    port: int = 5432
    host: str = "localhost"
    echo: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="PG_",
        extra="ignore",
    )

    @property
    def get_database_URL(self) -> str:
        return f"postgresql+psycopg_async://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    JWT_SECRET_KEY: str = "jwt_secret_key"
    JWT_REFRESH_SECRET_KEY: str = "jwt_refresh_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    redis: RedisConfig = Field(default_factory=RedisConfig)
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)


settings = Settings()
