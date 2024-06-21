from fastapi import FastAPI

from app.core.config import settings


main_app = FastAPI(title=settings.app_title)
