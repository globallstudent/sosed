from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "Sosed"
    debug: bool = False

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "sosed"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    jwt_secret_key: str = "change-the-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    email_verification_expire_hours: int = 24
    unverified_user_retention_hours: int = 48
    post_retention_days: int = 0

    redis_host: str = "localhost"
    redis_port: int = 6379

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "no-reply@sosed.local"
    smtp_tls: bool = False
    app_base_url: str = "http://localhost:8000"

    login_rate_limit: str = "5/minute"

    def _postgres_url(self, driver: str) -> str:
        return (
            f"postgresql+{driver}://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url(self) -> str:
        return self._postgres_url("asyncpg")

    @property
    def database_url_sync(self) -> str:
        return self._postgres_url("psycopg")

    @property
    def celery_broker_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_result_backend(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/1"

    @property
    def rate_limit_storage_uri(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/2"


@lru_cache
def get_settings() -> Settings:
    return Settings()
