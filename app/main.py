from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api import image_router, project_router
from app.core import db
from app.core.config import settings
from app.pages import pages_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db.dispose()

main_app = FastAPI(title=settings.app_title, lifespan=lifespan)
main_app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
main_app.mount('/static', StaticFiles(directory='app/static', html=True), name='static')
main_app.include_router(image_router)
main_app.include_router(project_router)
main_app.include_router(pages_router)
