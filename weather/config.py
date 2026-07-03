from dataclasses import dataclass
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True)
class YandexCredentials:
    login: str
    password: str
    api_key: str
    token: str
    id: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = Field(default="django-insecure-dev-only", validation_alias="SECRET_KEY")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", validation_alias="ALLOWED_HOSTS")

    db_engine: str = Field(default="django.db.backends.postgresql", validation_alias="DB_ENGINE")
    db_name: str = Field(default="", validation_alias="DB_NAME")
    db_user: str = Field(default="postgres", validation_alias="DB_USER")
    db_password: str = Field(default="", validation_alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")

    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="CELERY_BROKER_URL",
    )

    csv_delimiter: str = Field(default="#", validation_alias="CSV_DELIMITER")
    static_data_path: str = Field(default="static/csv_data/", validation_alias="STATIC_DATA_PATH")

    yandex_login: str = Field(default="", validation_alias="YANDEX_LOGIN")
    yandex_password: str = Field(default="", validation_alias="YANDEX_PASSWORD")
    yandex_api_key: str = Field(default="", validation_alias="YANDEX_API_KEY")
    yandex_token: str = Field(default="", validation_alias="YANDEX_TOKEN")
    yandex_id: str = Field(default="", validation_alias="YANDEX_ID")

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def database_configured(self) -> bool:
        return bool(self.db_name)

    @property
    def yandex(self) -> YandexCredentials:
        return YandexCredentials(
            login=self.yandex_login,
            password=self.yandex_password,
            api_key=self.yandex_api_key,
            token=self.yandex_token,
            id=self.yandex_id,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
