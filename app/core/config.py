from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    app_title = 'Тестовое LITE-Gallery'


settings = Settings()
