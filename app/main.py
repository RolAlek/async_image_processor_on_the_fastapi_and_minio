from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import image_router, project_router
from app.core import db
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db.dispose()

main_app = FastAPI(title=settings.app_title, lifespan=lifespan)
main_app.include_router(image_router)
main_app.include_router(project_router)
