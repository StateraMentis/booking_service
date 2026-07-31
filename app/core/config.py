from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения
    """

    # === Общие настройки ===
    app_name: str = Field("Meeting Room Booking Service", validation_alias="APP_NAME")
    app_version: str = Field("1.0.0", validation_alias="APP_VERSION")
    debug: bool = Field(False, validation_alias="DEBUG")
    enviroment: str = Field("development", validation_alias="ENVIRONMENT")

    # === База данных ===
    postgres_host: str = Field("db", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")
    postgres_user: str = Field("postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("postgres", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("meeting_room_db", validation_alias="POSTGRES_DB")
    database_url: str | None = Field(None, validation_alias="DATABASE_URL")

    # === JWT ===
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    algorithm: str = Field("HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def build_database_url(cls, v: str | None, info) -> str:
        """
        Собирает database_url из компонентов, если не задан явно
        """

        if v:
            return v

        data = info.data
        return (
            f"postgresql://{data.get('postgres_user')}:"
            f"{data.get('postgres_password')}@"
            f"{data.get('postgres_host')}:"
            f"{data.get('postgres_port')}/"
            f"{data.get('postgres_db')}"
        )

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
