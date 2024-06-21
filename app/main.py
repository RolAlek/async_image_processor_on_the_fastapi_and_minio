from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import image_router
from core import db
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db.dispose()

main_app = FastAPI(title=settings.app_title, lifespan=lifespan)
main_app.include_router(image_router)
