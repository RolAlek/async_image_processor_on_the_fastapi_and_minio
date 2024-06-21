from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False


class MinioConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False,
        env_nested_delimiter='__',
        env_prefix='APP_CONF__',
        extra='allow',
    )

    app_title: str = 'Тестовое LITE-Gallery'
    db: DatabaseConfig
    minio: MinioConfig


settings = Settings()
